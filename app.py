import os, io, base64, json
from typing import Dict, Any
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from PIL import Image
from openai import OpenAI

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
