"""
DEPRECATED: This file is kept for backward compatibility.
Please use: uvicorn backend.main:app --reload

The application has been refactored into modular files in the backend/ directory:
- backend/main.py: FastAPI app and routes
- backend/models.py: Pydantic models
- backend/schemas.py: OpenAI JSON schemas
- backend/llm.py: LLM service layer
- backend/nutrition.py: Nutrition calculations
- backend/routes.py: Route handlers
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

# Import the new modular app
from backend.main import app

print("⚠️  WARNING: Running from deprecated app.py")
print("✅ Please use: uvicorn backend.main:app --reload")
print("📁 New structure: backend/main.py, backend/models.py, backend/llm.py, etc.")
print("")

# Expose the app for backward compatibility
__all__ = ['app']
