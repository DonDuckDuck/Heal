"""
API route handlers
"""
from fastapi import File, UploadFile, HTTPException
from fastapi.responses import JSONResponse

from .models import (
    BudgetRequest,
    CompareMealRequest,
    SuggestionsRequest,
    CopyRequest,
    DailySummaryRequest,
)
from .nutrition import calculate_budget
from .llm import (
    img_to_data_uri,
    estimate_food_from_image,
    compare_meal_to_targets,
    generate_meal_suggestions,
    generate_reminder_copy,
    generate_daily_summary,
)


async def estimate_meal(image: UploadFile = File(None)):
    """
    POST /estimate
    Upload food photo → get calorie and macro estimate
    """
    from fastapi import Request
    try:
        # Try standard UploadFile first
        if image is not None and image.filename:
            print(f"📸 Received via UploadFile: {image.filename}")
            contents = await image.read()
        else:
            # Fallback: parse multipart manually
            print("⚠️  UploadFile is None, trying manual multipart parsing...")
            raise HTTPException(status_code=400, detail="Image parameter missing - check multipart format")
        
        print(f"📦 Image size: {len(contents)} bytes")
        
        if len(contents) == 0:
            raise HTTPException(status_code=400, detail="Empty image file")
        
        # Convert to data URI
        from io import BytesIO
        from PIL import Image as PILImage
        import base64
        
        try:
            im = PILImage.open(BytesIO(contents)).convert("RGB")
        except Exception as e:
            raise HTTPException(status_code=415, detail=f"Invalid image: {str(e)}")
        
        buf = BytesIO()
        im.save(buf, format="JPEG", quality=92)
        b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
        data_uri = f"data:image/jpeg;base64,{b64}"
        
        print(f"✅ Image converted to data URI, length: {len(data_uri)}")
        
        payload = estimate_food_from_image(data_uri)
        print(f"✅ GPT-4o analysis complete")
        
        return JSONResponse(payload)
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {str(e)}")


def calc_budget_endpoint(req: BudgetRequest):
    """
    POST /budget
    Calculate daily calorie and macro budget + per-meal targets
    """
    try:
        result = calculate_budget(
            height_cm=req.height_cm,
            weight_kg=req.weight_kg,
            age=req.age,
            sex=req.sex,
            exercise_level=req.exercise_level,
            diabetes_type=req.diabetes_type,
            meals_per_day=req.meals_per_day,
        )
        return JSONResponse(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def compare_meal_endpoint(req: CompareMealRequest):
    """
    POST /llm/compare
    Compare current meal against per-meal and daily targets
    """
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
        result = compare_meal_to_targets(payload)
        return JSONResponse(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def suggestions_endpoint(req: SuggestionsRequest):
    """
    POST /llm/suggestions
    Generate actionable meal suggestions
    """
    try:
        print(f"📝 Generating suggestions for meal: {req.meal_name}")
        payload = {
            "estimate": req.estimate,
            "per_meal_targets": req.per_meal_targets.model_dump(),
            "daily_remaining": req.daily_remaining.model_dump(),
            "meal_name": req.meal_name,
            "diabetes_type": req.diabetes_type,
        }
        print(f"   Payload keys: {list(payload.keys())}")
        result = generate_meal_suggestions(payload)
        print(f"✅ Suggestions endpoint complete")
        return JSONResponse(result)
    except Exception as e:
        print(f"❌ Error in suggestions_endpoint: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {str(e)}")


def copy_endpoint(req: CopyRequest):
    """
    POST /llm/copy
    Generate short notification copy
    """
    try:
        payload = req.model_dump()
        result = generate_reminder_copy(payload)
        return JSONResponse(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def daily_summary_endpoint(req: DailySummaryRequest):
    """
    POST /llm/daily_summary
    Generate end-of-day summary
    """
    try:
        payload = req.model_dump()
        result = generate_daily_summary(payload)
        return JSONResponse(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

