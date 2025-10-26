"""
OpenAI JSON schema definitions for structured outputs
"""
from typing import Dict, Any


def food_estimate_schema() -> Dict[str, Any]:
    """Schema for food photo → calorie/macro estimation"""
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
                                "name": {"type": "string"},
                                "display_name": {"type": "string"},
                                "category": {"type": "string"},
                                "cooking_method": {"type": "string"},
                                "grams": {"type": "number"},
                                "kcal": {"type": "number"},
                                "nutrition_per_100g": {
                                    "type": "object",
                                    "additionalProperties": False,
                                    "properties": {
                                        "kcal": {"type": "number"},
                                        "protein_g": {"type": "number"},
                                        "fat_g": {"type": "number"},
                                        "carb_g": {"type": "number"}
                                    },
                                    "required": ["kcal", "protein_g", "fat_g", "carb_g"]
                                },
                                "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                                "notes": {"type": "array", "items": {"type": "string"}}
                            }
                        }
                    },
                    "totals": {
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
                    "calories_range": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "low": {"type": "number"},
                            "high": {"type": "number"}
                        },
                        "required": ["low", "high"]
                    },
                    "assumptions": {"type": "array", "items": {"type": "string"}},
                    "warnings": {"type": "array", "items": {"type": "string"}},
                    "model_info": {"type": "string"}
                },
                "required": ["items", "totals", "calories_range", "assumptions", "warnings", "model_info"]
            }
        }
    }


def meal_compare_schema() -> Dict[str, Any]:
    """Schema for comparing meal against targets"""
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
                            "per_meal_percent": {
                                "type": "object",
                                "additionalProperties": False,
                                "properties": {
                                    "protein_g": {"type": "number"},
                                    "carb_g": {"type": "number"},
                                    "fat_g": {"type": "number"}
                                },
                                "required": ["protein_g", "carb_g", "fat_g"]
                            },
                            "daily_percent_after_meal": {
                                "type": "object",
                                "additionalProperties": False,
                                "properties": {
                                    "protein_g": {"type": "number"},
                                    "carb_g": {"type": "number"},
                                    "fat_g": {"type": "number"}
                                },
                                "required": ["protein_g", "carb_g", "fat_g"]
                            }
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


def suggestions_schema() -> Dict[str, Any]:
    """Schema for actionable meal suggestions"""
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
                                "text": {"type": "string"}
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


def reminder_copy_schema() -> Dict[str, Any]:
    """Schema for notification copy generation"""
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


def daily_summary_schema() -> Dict[str, Any]:
    """Schema for end-of-day summary"""
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

