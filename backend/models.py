"""
Pydantic models for request/response validation
"""
from typing import Optional, Literal, List, Dict, Any
from pydantic import BaseModel, Field


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


class CompareMealRequest(BaseModel):
    per_meal_targets: Macros
    daily_targets: Macros
    daily_consumed_so_far: Macros
    current_meal: Macros
    meal_index: int = Field(..., ge=1)
    meals_per_day: int = Field(..., ge=1)
    meal_name: Optional[str] = None
    diabetes_type: Optional[Literal["T1D", "T2D", "unknown"]] = None


class SuggestionsRequest(BaseModel):
    estimate: Dict[str, Any]
    per_meal_targets: Macros
    daily_remaining: Macros
    meal_name: Optional[str] = None
    diabetes_type: Optional[Literal["T1D", "T2D", "unknown"]] = None


class CopyRequest(BaseModel):
    type: Literal["photo_reminder", "over_limit"]
    locale: Optional[str] = "en"
    user_name: Optional[str] = None
    meal_name: Optional[str] = None
    meals_per_day: Optional[int] = None
    tone: Optional[Literal["friendly", "coach", "neutral", "playful"]] = "friendly"
    over_limit: Optional[Dict[str, float]] = None  # e.g., {"protein_g": 12, "carb_g": 30}


class DailySummaryRequest(BaseModel):
    date: Optional[str] = None
    diabetes_type: Optional[Literal["T1D", "T2D", "unknown"]] = None
    meals: List[Dict[str, Any]]
    daily_targets: Macros
    total_consumed: Macros
    flags: Optional[Dict[str, Any]] = None
    notes: Optional[List[str]] = None

