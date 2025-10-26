"""
LLM service layer - all OpenAI calls
"""
import os
import json
import io
import base64
from typing import Dict, Any
from PIL import Image
from openai import OpenAI
from fastapi import UploadFile, HTTPException

from .schemas import (
    food_estimate_schema,
    meal_compare_schema,
    suggestions_schema,
    reminder_copy_schema,
    daily_summary_schema,
)

# -------- Config --------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("Set OPENAI_API_KEY env var.")

client = OpenAI(api_key=OPENAI_API_KEY)


# -------- Image Processing --------
def img_to_data_uri(upload: UploadFile) -> str:
    """Convert uploaded image to JPEG data URI"""
    upload.file.seek(0)  # Reset file pointer
    raw = upload.file.read()
    if not raw:
        raise HTTPException(status_code=400, detail="Empty image file.")
    try:
        im = Image.open(io.BytesIO(raw)).convert("RGB")
    except Exception as e:
        raise HTTPException(status_code=415, detail=f"Unsupported image file: {str(e)}")
    buf = io.BytesIO()
    im.save(buf, format="JPEG", quality=92)
    b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    return f"data:image/jpeg;base64,{b64}"


# -------- LLM Calls --------
FOOD_ESTIMATE_PROMPT = (
    "You are a nutrition analyst. Given a single food photo, do EVERYTHING end-to-end: "
    "1) identify all major foods (<=6), across any cuisine; 2) estimate portion size in grams by "
    "visually referencing plate scale and typical serving geometry; 3) infer cooking method; "
    "4) pick typical nutrition density per 100g from general knowledge (USDA-like averages); "
    "5) compute per-item kcal/macros and totals; 6) provide a conservative low/high range. "
    "If breaded & fried, decompose into protein + breading + absorbed oil. "
    "If sauces or mixed dishes exist, include a generic sauce/mixture line with reasonable density. "
    "Always populate every field in the schema (use empty strings or [] when unsure) and output ONLY JSON per the provided schema—no explanations."
)


def estimate_food_from_image(image_data_uri: str) -> Dict[str, Any]:
    """Call GPT-4o to analyze food photo and return nutrition estimate"""
    resp = client.chat.completions.create(
        model="gpt-4o",
        temperature=0.2,
        response_format=food_estimate_schema(),
        messages=[
            {"role": "system", "content": FOOD_ESTIMATE_PROMPT},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Analyze this food photo and return JSON only."},
                    {"type": "image_url", "image_url": {"url": image_data_uri, "detail": "high"}}
                ]
            }
        ],
        timeout=60_000
    )
    return json.loads(resp.choices[0].message.content)


COMPARE_PROMPT = (
    "You are a diabetes nutrition coach. Compare the provided meal macros against BOTH per-meal targets and daily targets."
    " Compute exact differences and percentages using only the provided numbers."
    " Return ONLY JSON per the schema."
)


def compare_meal_to_targets(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Compare current meal against per-meal and daily targets"""
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        response_format=meal_compare_schema(),
        messages=[
            {"role": "system", "content": COMPARE_PROMPT},
            {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
        ],
        timeout=45_000,
    )
    return json.loads(resp.choices[0].message.content)


SUGGESTIONS_PROMPT = (
    "You are a diabetes-friendly nutrition coach. Using the meal estimate and current targets,"
    " propose immediately actionable steps the user can implement NOW: reduce/increase portions,"
    " swap sides, change order of eating (protein/veg first), add fiber/veg, hydration, and timing tips."
    " Keep actions specific with quantities in grams where possible. Return ONLY JSON."
)


def generate_meal_suggestions(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Generate actionable suggestions for the current meal"""
    try:
        print(f"🤖 Calling GPT-4o-mini for suggestions...")
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.2,
            response_format=suggestions_schema(),
            messages=[
                {"role": "system", "content": SUGGESTIONS_PROMPT},
                {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
            ],
            timeout=60_000,
        )
        result = json.loads(resp.choices[0].message.content)
        print(f"✅ Suggestions generated: {len(result.get('actions', []))} actions")
        return result
    except Exception as e:
        print(f"❌ Error generating suggestions: {type(e).__name__}: {str(e)}")
        raise


REMINDER_PROMPT = (
    "You are writing ultra-short notification copy. Generate concise, friendly lines."
    " For photo reminders: include placeholder {meal_name}. Keep each < 80 characters."
    " For over-limit: include dynamic numbers like {carb_excess_g}. Provide 3–5 variants."
    " Return ONLY JSON."
)


def generate_reminder_copy(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Generate short notification copy for reminders"""
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.5,
        response_format=reminder_copy_schema(),
        messages=[
            {"role": "system", "content": REMINDER_PROMPT},
            {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
        ],
        timeout=45_000,
    )
    return json.loads(resp.choices[0].message.content)


SUMMARY_PROMPT = (
    "You are a supportive diabetes nutrition coach. Summarize the day in 3–4 bullets,"
    " then provide 3–4 actionable focuses for tomorrow. Use simple language."
    " Reflect on macros vs targets, meal timing, fiber/veg, hydration, and carb distribution."
    " Return ONLY JSON."
)


def generate_daily_summary(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Generate end-of-day summary and next-day focus"""
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.2,
        response_format=daily_summary_schema(),
        messages=[
            {"role": "system", "content": SUMMARY_PROMPT},
            {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
        ],
        timeout=60_000,
    )
    return json.loads(resp.choices[0].message.content)

