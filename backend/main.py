"""
FastAPI application entry point
"""
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

from .routes import (
    estimate_meal,
    calc_budget_endpoint,
    compare_meal_endpoint,
    suggestions_endpoint,
    copy_endpoint,
    daily_summary_endpoint,
)
from .models import (
    BudgetRequest,
    CompareMealRequest,
    SuggestionsRequest,
    CopyRequest,
    DailySummaryRequest,
)

app = FastAPI(title="Heal - Diabetes Nutrition Assistant")

# CORS for iOS app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------- Routes --------
from fastapi import Request, Form

@app.post("/estimate")
async def estimate(request: Request, image: UploadFile = File(None)):
    # Debug: print all form fields
    try:
        form_data = await request.form()
        print(f"📋 Form fields received: {list(form_data.keys())}")
        
        # Try to get image from different possible field names
        img = form_data.get("image") or form_data.get("file") or form_data.get("photo")
        
        if img and hasattr(img, 'read'):
            print(f"✅ Found image in form_data under key: {[k for k in form_data.keys() if form_data[k] == img][0]}")
            return await estimate_meal(img)
        elif image:
            return await estimate_meal(image)
        else:
            print(f"❌ No image found. Form keys: {list(form_data.keys())}")
            raise HTTPException(status_code=400, detail=f"No image file in form data. Received keys: {list(form_data.keys())}")
    except Exception as e:
        print(f"❌ Error parsing form: {e}")
        raise


@app.post("/budget")
def budget(req: BudgetRequest):
    return calc_budget_endpoint(req)


@app.post("/llm/compare")
def compare(req: CompareMealRequest):
    return compare_meal_endpoint(req)


@app.post("/llm/suggestions")
def suggestions(req: SuggestionsRequest):
    return suggestions_endpoint(req)


@app.post("/llm/copy")
def copy(req: CopyRequest):
    return copy_endpoint(req)


@app.post("/llm/daily_summary")
def daily_summary(req: DailySummaryRequest):
    return daily_summary_endpoint(req)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/test-upload")
async def test_upload(image: UploadFile = File(None)):
    """Test endpoint to debug image upload"""
    from fastapi import Request
    if image is None:
        return {"error": "No image received", "image_param": "None"}
    
    contents = await image.read()
    return {
        "success": True,
        "filename": image.filename,
        "content_type": image.content_type,
        "size": len(contents),
        "first_bytes": contents[:20].hex() if contents else "empty"
    }

