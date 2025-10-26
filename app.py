import os, io, base64, json
from typing import Dict, Any, List, Optional, Literal
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from PIL import Image
from openai import OpenAI
from pydantic import BaseModel, Field

# -------- Config --------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("Set OPENAI_API_KEY env var.")
client = OpenAI(api_key=OPENAI_API_KEY)

app = FastAPI(title="Image→Calories (ChatGPT E2E)")

# -------- Helpers --------
def img_to_data_uri(upload: UploadFile) -> str:
    # 统一转为 JPEG，避免花式格式/EXIF 问题
    raw = upload.file.read()
    try:
        im = Image.open(io.BytesIO(raw)).convert("RGB")
    except Exception:
        raise HTTPException(status_code=415, detail="Unsupported image file.")
    buf = io.BytesIO()
    im.save(buf, format="JPEG", quality=92)
    b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    return f"data:image/jpeg;base64,{b64}"

def schema_response_format() -> Dict[str, Any]:
    # 让模型“只返回 JSON”，并且结构固定，适合直接给前端/服务消费
    # 说明：
    # - nutrition_per_100g 为模型给出的参考值（kcal/protein/fat/carb）
    # - calories_range 为不确定性区间（可直接用于 UI 或风控）
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "calorie_estimate",
            "strict": True,
            "schema": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "items": {
                        "type": "array",
                        "maxItems": 8,
                        "items": {
                            "type": "object",
                            "required": [
                                "name",
                                "display_name",
                                "category",
                                "cooking_method",
                                "grams",
                                "kcal",
                                "nutrition_per_100g",
                                "confidence",
                                "notes"
                            ],
                            "additionalProperties": False,
                            "properties": {
                                "name": {"type":"string"},              # 统一后的食物名（模型自行归一）
                                "display_name": {"type":"string"},      # 更口语的展示名
                                "category": {"type":"string"},          # protein/carb/veg/sauce/dessert/other
                                "cooking_method": {"type":"string"},    # fried/boiled/steamed/baked/raw/etc
                                "grams": {"type":"number"},             # 估计克重
                                "kcal": {"type":"number"},              # 该项热量
                                "nutrition_per_100g": {                 # 模型给的参考密度
                                    "type":"object",
                                    "additionalProperties": False,
                                    "properties": {
                                        "kcal":{"type":"number"},
                                        "protein_g":{"type":"number"},
                                        "fat_g":{"type":"number"},
                                        "carb_g":{"type":"number"}
                                    },
                                    "required": ["kcal","protein_g","fat_g","carb_g"]
                                },
                                "confidence": {"type":"number","minimum":0,"maximum":1},
                                "notes": {"type":"array","items":{"type":"string"}}
                            }
                        }
                    },
                    "totals": {
                        "type":"object",
                        "required": ["kcal","protein_g","fat_g","carb_g"],
                        "additionalProperties": False,
                        "properties": {
                            "kcal":{"type":"number"},
                            "protein_g":{"type":"number"},
                            "fat_g":{"type":"number"},
                            "carb_g":{"type":"number"}
                        }
                    },
                    "calories_range": {     # 不确定性（总热量）
                        "type":"object",
                        "additionalProperties": False,
                        "properties": {
                            "low":{"type":"number"},
                            "high":{"type":"number"}
                        },
                        "required": ["low","high"]
                    },
                    "assumptions": {"type":"array","items":{"type":"string"}},
                    "warnings": {"type":"array","items":{"type":"string"}},
                    "model_info": {"type":"string"}
                },
                "required": ["items","totals","calories_range","assumptions","warnings","model_info"]
            }
        }
    }

SYSTEM_PROMPT = (
    "You are a nutrition analyst. Given a single food photo, do EVERYTHING end-to-end: "
    "1) identify all major foods (<=6), across any cuisine; 2) estimate portion size in grams by "
    "visually referencing plate scale and typical serving geometry; 3) infer cooking method; "
    "4) pick typical nutrition density per 100g from general knowledge (USDA-like averages); "
    "5) compute per-item kcal/macros and totals; 6) provide a conservative low/high range. "
    "If breaded & fried, decompose into protein + breading + absorbed oil. "
    "If sauces or mixed dishes exist, include a generic sauce/mixture line with reasonable density. "
    "Always populate every field in the schema (use empty strings or [] when unsure) and output ONLY JSON per the provided schema—no explanations."
)

def call_model(image_data_uri: str) -> Dict[str, Any]:
    resp = client.chat.completions.create(
        model="gpt-4o",
        temperature=0.2,
        response_format=schema_response_format(),
        messages=[{
            "role":"system","content": SYSTEM_PROMPT
        },{
            "role":"user",
            "content": [
                {"type":"text","text":"Analyze this food photo and return JSON only."},
                {"type":"image_url","image_url":{"url": image_data_uri, "detail":"high"}}
            ]
        }],
        timeout=60_000
    )
    return json.loads(resp.choices[0].message.content)

# -------- API (single endpoint) --------
@app.post("/estimate")
async def estimate(image: UploadFile = File(...)):
    """
    输入：multipart/form-data 里的一张图片
    输出：JSON（分项与总热量+宏量营养+区间），完全由 ChatGPT 生成
    """
    try:
        data_uri = img_to_data_uri(image)
        payload = call_model(data_uri)
        return JSONResponse(payload)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# =============================
# Deterministic planning helpers
# =============================

class Macros(BaseModel):
    protein_g: float = Field(..., ge=0)
    fat_g: float = Field(..., ge=0)
    carb_g: float = Field(..., ge=0)
    kcal: Optional[float] = Field(None, ge=0)


class BudgetRequest(BaseModel):
    height_cm: float = Field(..., gt=0)
    weight_kg: float = Field(..., gt=0)
    age: int = Field(..., ge=10, le=120)
    sex: Literal["male", "female"]
    exercise_level: Literal["sedentary", "light", "moderate", "active", "very_active"]
    diabetes_type: Literal["T1D", "T2D", "unknown"] = "unknown"
    meals_per_day: int = Field(3, ge=1, le=8)


def _activity_factor(level: str) -> float:
    mapping = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725,
        "very_active": 1.9,
    }
    return mapping[level]


def _macro_split(diabetes_type: str) -> Dict[str, float]:
    # Conservative defaults; customize per user later
    if diabetes_type == "T2D":
        return {"protein": 0.30, "carb": 0.35, "fat": 0.35}
    if diabetes_type == "T1D":
        return {"protein": 0.25, "carb": 0.40, "fat": 0.35}
    return {"protein": 0.25, "carb": 0.45, "fat": 0.30}


@app.post("/budget")
def calc_budget(req: BudgetRequest):
    # Mifflin-St Jeor BMR
    bmr = 10 * req.weight_kg + 6.25 * req.height_cm - 5 * req.age + (5 if req.sex == "male" else -161)
    tdee = bmr * _activity_factor(req.exercise_level)
    splits = _macro_split(req.diabetes_type)
    protein_kcal = tdee * splits["protein"]
    carb_kcal = tdee * splits["carb"]
    fat_kcal = tdee * splits["fat"]
    daily = {
        "kcal": round(tdee, 1),
        "protein_g": round(protein_kcal / 4, 1),
        "carb_g": round(carb_kcal / 4, 1),
        "fat_g": round(fat_kcal / 9, 1),
    }
    per_meal = {
        "protein_g": round(daily["protein_g"] / req.meals_per_day, 1),
        "carb_g": round(daily["carb_g"] / req.meals_per_day, 1),
        "fat_g": round(daily["fat_g"] / req.meals_per_day, 1),
        "kcal": round(daily["kcal"] / req.meals_per_day, 1),
    }
    return {
        "daily_budget": daily,
        "per_meal_targets": per_meal,
        "macro_split": splits,
        "meals_per_day": req.meals_per_day,
    }


# =============================
# LLM functions (OpenAI only)
# =============================

def compare_schema() -> Dict[str, Any]:
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "meal_compare",
            "strict": True,
            "schema": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "per_meal_evaluation": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "protein_g": {
                                "type": "object",
                                "additionalProperties": False,
                                "properties": {
                                    "target": {"type": "number"},
                                    "actual": {"type": "number"},
                                    "difference": {"type": "number"},
                                    "status": {"type": "string"},
                                    "percent_of_target": {"type": "number"}
                                },
                                "required": ["target", "actual", "difference", "status", "percent_of_target"]
                            },
                            "carb_g": {
                                "type": "object",
                                "additionalProperties": False,
                                "properties": {
                                    "target": {"type": "number"},
                                    "actual": {"type": "number"},
                                    "difference": {"type": "number"},
                                    "status": {"type": "string"},
                                    "percent_of_target": {"type": "number"}
                                },
                                "required": ["target", "actual", "difference", "status", "percent_of_target"]
                            },
                            "fat_g": {
                                "type": "object",
                                "additionalProperties": False,
                                "properties": {
                                    "target": {"type": "number"},
                                    "actual": {"type": "number"},
                                    "difference": {"type": "number"},
                                    "status": {"type": "string"},
                                    "percent_of_target": {"type": "number"}
                                },
                                "required": ["target", "actual", "difference", "status", "percent_of_target"]
                            }
                        },
                        "required": ["protein_g", "carb_g", "fat_g"]
                    },
                    "daily_evaluation_post_meal": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "protein_g": {
                                "type": "object",
                                "additionalProperties": False,
                                "properties": {
                                    "target_daily": {"type": "number"},
                                    "consumed_so_far": {"type": "number"},
                                    "after_meal": {"type": "number"},
                                    "remaining": {"type": "number"},
                                    "will_exceed_by": {"type": "number"},
                                    "percent_of_daily_target_after_meal": {"type": "number"}
                                },
                                "required": ["target_daily", "consumed_so_far", "after_meal", "remaining", "will_exceed_by", "percent_of_daily_target_after_meal"]
                            },
                            "carb_g": {
                                "type": "object",
                                "additionalProperties": False,
                                "properties": {
                                    "target_daily": {"type": "number"},
                                    "consumed_so_far": {"type": "number"},
                                    "after_meal": {"type": "number"},
                                    "remaining": {"type": "number"},
                                    "will_exceed_by": {"type": "number"},
                                    "percent_of_daily_target_after_meal": {"type": "number"}
                                },
                                "required": ["target_daily", "consumed_so_far", "after_meal", "remaining", "will_exceed_by", "percent_of_daily_target_after_meal"]
                            },
                            "fat_g": {
                                "type": "object",
                                "additionalProperties": False,
                                "properties": {
                                    "target_daily": {"type": "number"},
                                    "consumed_so_far": {"type": "number"},
                                    "after_meal": {"type": "number"},
                                    "remaining": {"type": "number"},
                                    "will_exceed_by": {"type": "number"},
                                    "percent_of_daily_target_after_meal": {"type": "number"}
                                },
                                "required": ["target_daily", "consumed_so_far", "after_meal", "remaining", "will_exceed_by", "percent_of_daily_target_after_meal"]
                            }
                        },
                        "required": ["protein_g", "carb_g", "fat_g"]
                    },
                    "flags": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "per_meal_exceeded_any": {"type": "boolean"},
                            "daily_exceeded_any": {"type": "boolean"},
                            "over_per_meal": {"type": "array", "items": {"type": "string"}},
                            "over_daily": {"type": "array", "items": {"type": "string"}}
                        },
                        "required": ["per_meal_exceeded_any", "daily_exceeded_any", "over_per_meal", "over_daily"]
                    },
                    "progress_bars": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "per_meal_percent": {"type": "object", "additionalProperties": False, "properties": {"protein_g": {"type": "number"}, "carb_g": {"type": "number"}, "fat_g": {"type": "number"}}, "required": ["protein_g", "carb_g", "fat_g"]},
                            "daily_percent_after_meal": {"type": "object", "additionalProperties": False, "properties": {"protein_g": {"type": "number"}, "carb_g": {"type": "number"}, "fat_g": {"type": "number"}}, "required": ["protein_g", "carb_g", "fat_g"]}
                        },
                        "required": ["per_meal_percent", "daily_percent_after_meal"]
                    },
                    "notes": {"type": "array", "items": {"type": "string"}},
                    "model_info": {"type": "string"}
                },
                "required": ["per_meal_evaluation", "daily_evaluation_post_meal", "flags", "progress_bars", "notes", "model_info"]
            }
        }
    }


COMPARE_SYSTEM_PROMPT = (
    "You are a diabetes nutrition coach. Compare the provided meal macros against BOTH per-meal targets and daily targets."
    " Compute exact differences and percentages using only the provided numbers."
    " Return ONLY JSON per the schema."
)


class CompareMealRequest(BaseModel):
    per_meal_targets: Macros
    daily_targets: Macros
    daily_consumed_so_far: Macros
    current_meal: Macros
    meal_index: int = Field(..., ge=1)
    meals_per_day: int = Field(..., ge=1)
    meal_name: Optional[str] = None
    diabetes_type: Optional[Literal["T1D", "T2D", "unknown"]] = None


@app.post("/llm/compare")
def llm_compare(req: CompareMealRequest):
    try:
        payload = {
            "per_meal_targets": req.per_meal_targets.model_dump(),
            "daily_targets": req.daily_targets.model_dump(),
            "daily_consumed_so_far": req.daily_consumed_so_far.model_dump(),
            "current_meal": req.current_meal.model_dump(),
            "meal_index": req.meal_index,
            "meals_per_day": req.meals_per_day,
            "meal_name": req.meal_name,
            "diabetes_type": req.diabetes_type,
        }
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0,
            response_format=compare_schema(),
            messages=[
                {"role": "system", "content": COMPARE_SYSTEM_PROMPT},
                {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
            ],
            timeout=45_000,
        )
        return JSONResponse(json.loads(resp.choices[0].message.content))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def suggestions_schema() -> Dict[str, Any]:
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "meal_suggestions",
            "strict": True,
            "schema": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "actions": {
                        "type": "array",
                        "maxItems": 8,
                        "items": {
                            "type": "object",
                            "required": ["kind", "text"],
                            "additionalProperties": False,
                            "properties": {
                                "kind": {"type": "string", "enum": ["portion", "swap", "timing", "order", "add", "remove", "other"]},
                                "text": {"type": "string"},
                                "estimated_effect": {
                                    "type": "object",
                                    "additionalProperties": False,
                                    "properties": {
                                        "kcal": {"type": "number"},
                                        "protein_g": {"type": "number"},
                                        "fat_g": {"type": "number"},
                                        "carb_g": {"type": "number"}
                                    }
                                }
                            }
                        }
                    },
                    "adjusted_macros_after_actions": {
                        "type": "object",
                        "required": ["kcal", "protein_g", "fat_g", "carb_g"],
                        "additionalProperties": False,
                        "properties": {
                            "kcal": {"type": "number"},
                            "protein_g": {"type": "number"},
                            "fat_g": {"type": "number"},
                            "carb_g": {"type": "number"}
                        }
                    },
                    "rationale": {"type": "array", "items": {"type": "string"}},
                    "model_info": {"type": "string"}
                },
                "required": ["actions", "adjusted_macros_after_actions", "rationale", "model_info"]
            }
        }
    }


SUGGESTIONS_SYSTEM_PROMPT = (
    "You are a diabetes-friendly nutrition coach. Using the meal estimate and current targets,"
    " propose immediately actionable steps the user can implement NOW: reduce/increase portions,"
    " swap sides, change order of eating (protein/veg first), add fiber/veg, hydration, and timing tips."
    " Keep actions specific with quantities in grams where possible. Return ONLY JSON."
)


class SuggestionsRequest(BaseModel):
    estimate: Dict[str, Any]
    per_meal_targets: Macros
    daily_remaining: Macros
    meal_name: Optional[str] = None
    diabetes_type: Optional[Literal["T1D", "T2D", "unknown"]] = None


@app.post("/llm/suggestions")
def llm_suggestions(req: SuggestionsRequest):
    try:
        payload = {
            "estimate": req.estimate,
            "per_meal_targets": req.per_meal_targets.model_dump(),
            "daily_remaining": req.daily_remaining.model_dump(),
            "meal_name": req.meal_name,
            "diabetes_type": req.diabetes_type,
        }
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.2,
            response_format=suggestions_schema(),
            messages=[
                {"role": "system", "content": SUGGESTIONS_SYSTEM_PROMPT},
                {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
            ],
            timeout=60_000,
        )
        return JSONResponse(json.loads(resp.choices[0].message.content))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def reminder_copy_schema() -> Dict[str, Any]:
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "reminder_copy",
            "strict": True,
            "schema": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "type": {"type": "string"},
                    "placeholders": {"type": "array", "items": {"type": "string"}},
                    "lines": {"type": "array", "maxItems": 7, "items": {"type": "string"}},
                    "model_info": {"type": "string"}
                },
                "required": ["type", "placeholders", "lines", "model_info"]
            }
        }
    }


REMINDER_SYSTEM_PROMPT = (
    "You are writing ultra-short notification copy. Generate concise, friendly lines."
    " For photo reminders: include placeholder {meal_name}. Keep each < 80 characters."
    " For over-limit: include dynamic numbers like {carb_excess_g}. Provide 3–5 variants."
    " Return ONLY JSON."
)


class CopyRequest(BaseModel):
    type: Literal["photo_reminder", "over_limit"]
    locale: Optional[str] = "en"
    user_name: Optional[str] = None
    meal_name: Optional[str] = None
    meals_per_day: Optional[int] = None
    tone: Optional[Literal["friendly", "coach", "neutral", "playful"]] = "friendly"
    over_limit: Optional[Dict[str, float]] = None  # e.g., {"protein_g": 12, "carb_g": 30}


@app.post("/llm/copy")
def llm_copy(req: CopyRequest):
    try:
        payload = req.model_dump()
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.5,
            response_format=reminder_copy_schema(),
            messages=[
                {"role": "system", "content": REMINDER_SYSTEM_PROMPT},
                {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
            ],
            timeout=45_000,
        )
        return JSONResponse(json.loads(resp.choices[0].message.content))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def daily_summary_schema() -> Dict[str, Any]:
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "daily_summary",
            "strict": True,
            "schema": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "summary_points": {"type": "array", "minItems": 3, "maxItems": 4, "items": {"type": "string"}},
                    "next_day_focus": {"type": "array", "minItems": 3, "maxItems": 4, "items": {"type": "string"}},
                    "macro_overview": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "protein_g": {"type": "string"},
                            "carb_g": {"type": "string"},
                            "fat_g": {"type": "string"}
                        },
                        "required": ["protein_g", "carb_g", "fat_g"]
                    },
                    "alerts": {"type": "array", "items": {"type": "string"}},
                    "model_info": {"type": "string"}
                },
                "required": ["summary_points", "next_day_focus", "macro_overview", "alerts", "model_info"]
            }
        }
    }


SUMMARY_SYSTEM_PROMPT = (
    "You are a supportive diabetes nutrition coach. Summarize the day in 3–4 bullets,"
    " then provide 3–4 actionable focuses for tomorrow. Use simple language."
    " Reflect on macros vs targets, meal timing, fiber/veg, hydration, and carb distribution."
    " Return ONLY JSON."
)


class DailySummaryRequest(BaseModel):
    date: Optional[str] = None
    diabetes_type: Optional[Literal["T1D", "T2D", "unknown"]] = None
    meals: List[Dict[str, Any]]
    daily_targets: Macros
    total_consumed: Macros
    flags: Optional[Dict[str, Any]] = None
    notes: Optional[List[str]] = None


@app.post("/llm/daily_summary")
def llm_daily_summary(req: DailySummaryRequest):
    try:
        payload = req.model_dump()
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.2,
            response_format=daily_summary_schema(),
            messages=[
                {"role": "system", "content": SUMMARY_SYSTEM_PROMPT},
                {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
            ],
            timeout=60_000,
        )
        return JSONResponse(json.loads(resp.choices[0].message.content))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
