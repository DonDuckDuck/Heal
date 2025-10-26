#!/usr/bin/env python3
"""
Simple test script to verify backend functionality
Run this after starting the server to test all endpoints
"""

import requests
import json
from pathlib import Path

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health check endpoint"""
    print("🔍 Testing /health...")
    resp = requests.get(f"{BASE_URL}/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
    print("✅ Health check passed")

def test_budget():
    """Test budget calculation"""
    print("\n🔍 Testing /budget...")
    data = {
        "height_cm": 170,
        "weight_kg": 70,
        "age": 30,
        "sex": "male",
        "exercise_level": "moderate",
        "diabetes_type": "T2D",
        "meals_per_day": 3
    }
    resp = requests.post(f"{BASE_URL}/budget", json=data)
    assert resp.status_code == 200
    result = resp.json()
    assert "daily_budget" in result
    assert "per_meal_targets" in result
    print(f"✅ Budget calculated:")
    print(f"   Daily: {result['daily_budget']['kcal']} kcal")
    print(f"   Per meal: {result['per_meal_targets']['kcal']} kcal")
    return result

def test_estimate():
    """Test food estimation (requires image)"""
    print("\n🔍 Testing /estimate...")
    
    # Look for a test image
    test_images = ["food.jpg", "a_whole_pig.png", "Binghongcha.png"]
    image_path = None
    for img in test_images:
        path = Path(img)
        if path.exists():
            image_path = path
            break
    
    if not image_path:
        print("⚠️  No test image found, skipping estimation test")
        return None
    
    print(f"   Using image: {image_path}")
    with open(image_path, "rb") as f:
        files = {"image": (image_path.name, f, "image/jpeg")}
        resp = requests.post(f"{BASE_URL}/estimate", files=files, timeout=120)
    
    assert resp.status_code == 200
    result = resp.json()
    assert "totals" in result
    assert "items" in result
    print(f"✅ Food estimated:")
    print(f"   Total: {result['totals']['kcal']} kcal")
    print(f"   Items: {len(result['items'])} foods detected")
    for item in result['items'][:3]:
        print(f"     - {item['display_name']}: {item['kcal']} kcal")
    return result

def test_compare(budget, estimate):
    """Test meal comparison"""
    if not budget or not estimate:
        print("\n⚠️  Skipping comparison test (missing budget or estimate)")
        return None
    
    print("\n🔍 Testing /llm/compare...")
    data = {
        "per_meal_targets": budget["per_meal_targets"],
        "daily_targets": budget["daily_budget"],
        "daily_consumed_so_far": {
            "protein_g": 0,
            "fat_g": 0,
            "carb_g": 0,
            "kcal": 0
        },
        "current_meal": estimate["totals"],
        "meal_index": 1,
        "meals_per_day": 3,
        "meal_name": "Breakfast",
        "diabetes_type": "T2D"
    }
    resp = requests.post(f"{BASE_URL}/llm/compare", json=data, timeout=60)
    assert resp.status_code == 200
    result = resp.json()
    assert "flags" in result
    print(f"✅ Comparison complete:")
    print(f"   Per-meal exceeded: {result['flags']['per_meal_exceeded_any']}")
    print(f"   Daily exceeded: {result['flags']['daily_exceeded_any']}")
    return result

def test_suggestions(budget, estimate):
    """Test suggestions generation"""
    if not budget or not estimate:
        print("\n⚠️  Skipping suggestions test (missing budget or estimate)")
        return None
    
    print("\n🔍 Testing /llm/suggestions...")
    data = {
        "estimate": estimate,
        "per_meal_targets": budget["per_meal_targets"],
        "daily_remaining": budget["daily_budget"],
        "meal_name": "Breakfast",
        "diabetes_type": "T2D"
    }
    resp = requests.post(f"{BASE_URL}/llm/suggestions", json=data, timeout=60)
    assert resp.status_code == 200
    result = resp.json()
    assert "actions" in result
    print(f"✅ Suggestions generated:")
    print(f"   Actions: {len(result['actions'])} recommendations")
    for i, action in enumerate(result['actions'][:3], 1):
        print(f"     {i}. [{action['kind']}] {action['text'][:60]}...")
    return result

def test_daily_summary(budget, estimate):
    """Test daily summary generation"""
    if not budget or not estimate:
        print("\n⚠️  Skipping summary test (missing budget or estimate)")
        return
    
    print("\n🔍 Testing /llm/daily_summary...")
    data = {
        "date": "2025-10-26",
        "diabetes_type": "T2D",
        "meals": [
            {
                "timestamp": "2025-10-26T08:00:00",
                "meal_name": "Breakfast",
                "macros": estimate["totals"],
                "estimate": estimate
            }
        ],
        "daily_targets": budget["daily_budget"],
        "total_consumed": estimate["totals"]
    }
    resp = requests.post(f"{BASE_URL}/llm/daily_summary", json=data, timeout=60)
    assert resp.status_code == 200
    result = resp.json()
    assert "summary_points" in result
    assert "next_day_focus" in result
    print(f"✅ Daily summary generated:")
    print(f"   Summary points: {len(result['summary_points'])}")
    for point in result['summary_points']:
        print(f"     • {point}")
    print(f"   Next day focus: {len(result['next_day_focus'])}")
    for focus in result['next_day_focus']:
        print(f"     → {focus}")

def main():
    print("=" * 60)
    print("🏥 Heal Backend Test Suite")
    print("=" * 60)
    
    try:
        # Basic tests
        test_health()
        budget = test_budget()
        estimate = test_estimate()
        
        # LLM tests (only if estimate succeeded)
        comparison = test_compare(budget, estimate)
        suggestions = test_suggestions(budget, estimate)
        test_daily_summary(budget, estimate)
        
        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to backend")
        print("   Make sure the server is running:")
        print("   ./start_server.sh")
        print("   or")
        print("   uvicorn backend.main:app --reload")
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

