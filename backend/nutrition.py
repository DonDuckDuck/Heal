"""
Deterministic nutrition calculations (calorie budget, macro splits)
"""
from typing import Dict


def activity_factor(level: str) -> float:
    """Convert activity level to TDEE multiplier"""
    mapping = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725,
        "very_active": 1.9,
    }
    return mapping.get(level, 1.2)


def macro_split(diabetes_type: str) -> Dict[str, float]:
    """
    Return macro percentage splits optimized for diabetes type.
    Conservative defaults; can be personalized later.
    """
    if diabetes_type == "T2D":
        return {"protein": 0.30, "carb": 0.35, "fat": 0.35}
    if diabetes_type == "T1D":
        return {"protein": 0.25, "carb": 0.40, "fat": 0.35}
    return {"protein": 0.25, "carb": 0.45, "fat": 0.30}


def calculate_budget(
    height_cm: float,
    weight_kg: float,
    age: int,
    sex: str,
    exercise_level: str,
    diabetes_type: str,
    meals_per_day: int = 3
) -> Dict:
    """
    Calculate daily calorie budget and macro targets using Mifflin-St Jeor.
    Returns daily and per-meal targets.
    """
    # Mifflin-St Jeor BMR
    bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + (5 if sex == "male" else -161)
    tdee = bmr * activity_factor(exercise_level)
    
    splits = macro_split(diabetes_type)
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
        "protein_g": round(daily["protein_g"] / meals_per_day, 1),
        "carb_g": round(daily["carb_g"] / meals_per_day, 1),
        "fat_g": round(daily["fat_g"] / meals_per_day, 1),
        "kcal": round(daily["kcal"] / meals_per_day, 1),
    }
    
    return {
        "daily_budget": daily,
        "per_meal_targets": per_meal,
        "macro_split": splits,
        "meals_per_day": meals_per_day,
    }

