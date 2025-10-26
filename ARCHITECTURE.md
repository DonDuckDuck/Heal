# Heal - System Architecture

## Overview

Heal is a diabetes nutrition assistant that uses AI to automatically track meals via photos, provide real-time feedback, and deliver personalized insights. The system consists of a FastAPI backend (Python) and an iOS frontend (SwiftUI).

## System Flow

```
┌─────────────────────────────────────────────────────────────┐
│                         User Journey                         │
└─────────────────────────────────────────────────────────────┘

1. REGISTRATION
   User Input → iOS → POST /budget → Backend Calculates TDEE
   → Returns: Daily & Per-Meal Targets → Stored in iOS

2. MEAL TIME
   Camera → Photo → POST /estimate → GPT-4o Analyzes Image
   → Returns: Nutrition Data
   
   Then:
   Nutrition + Targets → POST /llm/compare → GPT-4o-mini
   → Returns: Comparison & Progress
   
   And:
   Nutrition + Targets → POST /llm/suggestions → GPT-4o-mini
   → Returns: Actionable Tips
   
3. SAVE MEAL
   iOS saves meal locally → Updates progress bars

4. END OF DAY (2hrs after last meal)
   All meals + targets → POST /llm/daily_summary → GPT-4o-mini
   → Returns: Day summary + Tomorrow's focus
```

## Architecture Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                        iOS App (SwiftUI)                      │
├──────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │Registration │  │   Camera    │  │   Today     │          │
│  │    View     │  │    View     │  │    View     │  ...     │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘          │
│         │                │                │                  │
│         └────────────────┼────────────────┘                  │
│                          │                                   │
│                 ┌────────▼────────┐                          │
│                 │   APIService    │                          │
│                 │  (URLSession)   │                          │
│                 └────────┬────────┘                          │
└──────────────────────────┼───────────────────────────────────┘
                           │ HTTP/JSON
                           │
┌──────────────────────────▼───────────────────────────────────┐
│                   FastAPI Backend (Python)                    │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                    main.py (App)                      │   │
│  │  ┌──────┐ ┌────────┐ ┌──────┐ ┌──────────┐ ┌──────┐ │   │
│  │  │/budget│ │/estimate│ │/compare│ │/suggestions│ │/summary││   │
│  │  └───┬──┘ └────┬───┘ └───┬──┘ └─────┬────┘ └───┬──┘ │   │
│  └──────┼─────────┼─────────┼──────────┼──────────┼────┘   │
│         │         │         │          │          │         │
│  ┌──────▼─────────▼─────────▼──────────▼──────────▼────┐   │
│  │              routes.py (Handlers)                     │   │
│  └──────┬─────────┬─────────┬──────────┬──────────┬────┘   │
│         │         │         │          │          │         │
│  ┌──────▼──┐  ┌───▼─────────▼──────────▼──────────▼────┐   │
│  │nutrition│  │         llm.py (OpenAI)                 │   │
│  │  .py    │  │  ┌──────────────────────────────────┐  │   │
│  │         │  │  │  GPT-4o: Image → Nutrition       │  │   │
│  │ TDEE    │  │  │  GPT-4o-mini: Text generation    │  │   │
│  │ BMR     │  │  └──────────────────────────────────┘  │   │
│  │ Macros  │  │                                         │   │
│  └─────────┘  └─────────────────────────────────────────┘   │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │         models.py (Pydantic validation)               │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │     schemas.py (OpenAI structured outputs)            │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
└───────────────────────────┬───────────────────────────────────┘
                            │
                   ┌────────▼─────────┐
                   │   OpenAI API     │
                   │  GPT-4o / 4o-mini│
                   └──────────────────┘
```

## Backend Components

### 1. `main.py` - Application Entry Point
- FastAPI app initialization
- CORS middleware for iOS
- Route registration
- Health check endpoint

### 2. `routes.py` - Route Handlers
- `estimate_meal()`: Handle image upload
- `calc_budget_endpoint()`: Calculate nutrition budget
- `compare_meal_endpoint()`: Compare meal to targets
- `suggestions_endpoint()`: Generate suggestions
- `daily_summary_endpoint()`: End-of-day summary

### 3. `llm.py` - LLM Service Layer
All OpenAI API calls with structured outputs:

- `estimate_food_from_image()`: GPT-4o vision analysis
- `compare_meal_to_targets()`: Meal vs target comparison
- `generate_meal_suggestions()`: Actionable recommendations
- `generate_reminder_copy()`: Notification text
- `generate_daily_summary()`: Daily insights

### 4. `nutrition.py` - Deterministic Calculations
- `activity_factor()`: Convert activity level to multiplier
- `macro_split()`: Diabetes-optimized macro percentages
- `calculate_budget()`: Mifflin-St Jeor BMR → TDEE → macros

### 5. `models.py` - Data Validation
Pydantic models for request/response validation:
- `BudgetRequest`, `CompareMealRequest`, `SuggestionsRequest`
- `CopyRequest`, `DailySummaryRequest`
- `Macros` (shared structure)

### 6. `schemas.py` - OpenAI JSON Schemas
Structured output schemas for reliable parsing:
- `food_estimate_schema()`: Nutrition breakdown
- `meal_compare_schema()`: Comparison results
- `suggestions_schema()`: Actionable steps
- `daily_summary_schema()`: Day summary

## iOS Components

### Models

**`AppState.swift`** - Global State Management
- User profile & budget
- Today's meals & consumed totals
- UserDefaults persistence

**`DataModels.swift`** - Data Structures
- `UserProfile`, `DailyBudget`, `Macros`
- `FoodEstimate`, `MealComparison`, `MealSuggestions`
- `DailySummary`, `MealRecord`

### Services

**`APIService.swift`** - Backend Integration
- `calculateBudget()`: POST /budget
- `estimateMeal()`: POST /estimate (multipart)
- `compareMeal()`: POST /llm/compare
- `getSuggestions()`: POST /llm/suggestions
- `getDailySummary()`: POST /llm/daily_summary

### Views

**`RegistrationView.swift`**
- Onboarding form
- Calls `/budget` endpoint
- Saves profile & budget

**`CameraView.swift`**
- Camera integration (UIImagePickerController)
- Photo capture → analysis → display results
- Shows nutrition, comparison, suggestions
- Save meal button

**`TodayView.swift`**
- Daily progress bars (protein/carb/fat)
- List of today's meals
- Visual feedback on targets

**`MainTabView.swift`**
- Tab navigation container
- 4 tabs: Today, Camera, Progress, Profile

**`ProfileView.swift`**
- Display user info
- Show daily budget
- Future: Edit settings

**`ProgressView.swift`**
- Placeholder for weekly trends
- Future: Charts & insights

## Data Flow Examples

### Example 1: Registration

```
iOS:  User fills form (height, weight, age, sex, exercise, diabetes type)
  ↓
iOS:  POST /budget with BudgetRequest
  ↓
Backend: nutrition.calculate_budget()
  → Mifflin-St Jeor BMR = 10*weight + 6.25*height - 5*age + sex_offset
  → TDEE = BMR * activity_factor
  → Split into protein/carb/fat based on diabetes type
  → Divide by meals_per_day for per-meal targets
  ↓
Backend: Returns DailyBudget JSON
  ↓
iOS:  Saves to UserDefaults + AppState
  → Navigate to MainTabView
```

### Example 2: Meal Photo Analysis

```
iOS:  User takes photo via camera
  ↓
iOS:  Convert to JPEG, create multipart/form-data
  ↓
iOS:  POST /estimate with image
  ↓
Backend: llm.estimate_food_from_image()
  → Convert to base64 data URI
  → Call GPT-4o with vision
  → Structured output: items[], totals, range
  ↓
iOS:  Receive FoodEstimate
  ↓
iOS:  POST /llm/compare with meal + targets
  ↓
Backend: llm.compare_meal_to_targets()
  → GPT-4o-mini calculates differences & percentages
  → Returns flags for exceeded targets
  ↓
iOS:  POST /llm/suggestions
  ↓
Backend: llm.generate_meal_suggestions()
  → GPT-4o-mini proposes portion changes, swaps, etc.
  ↓
iOS:  Display all results to user
  → User reviews, then saves or retakes
```

### Example 3: Daily Summary

```
iOS:  2 hours after last meal (scheduled notification)
  ↓
iOS:  POST /llm/daily_summary with all meals + targets
  ↓
Backend: llm.generate_daily_summary()
  → GPT-4o-mini analyzes full day
  → Returns 3-4 summary points
  → Returns 3-4 next-day focus items
  ↓
iOS:  Display summary as notification + in-app
```

## AI Model Usage

### GPT-4o (Vision)
- **Endpoint**: `/estimate`
- **Task**: Analyze food photos
- **Input**: High-res JPEG image
- **Output**: Structured JSON with items, macros, calories
- **Temperature**: 0.2 (low variance)
- **Timeout**: 60s

### GPT-4o-mini (Text)
- **Endpoints**: `/llm/compare`, `/llm/suggestions`, `/llm/daily_summary`
- **Task**: Text generation with structured outputs
- **Input**: JSON payloads
- **Output**: Structured JSON per schema
- **Temperature**: 0.0-0.5 depending on use case
- **Timeout**: 45-60s

## Security Considerations

### Current (MVP)
- API key in environment variable
- No user authentication
- Local data storage only
- CORS wide open for development

### Production Recommendations
1. **Authentication**: Add user accounts with JWT
2. **API Security**: Rate limiting, API key rotation
3. **Data Privacy**: Encrypt photos, comply with HIPAA if storing health data
4. **CORS**: Restrict to specific iOS bundle ID
5. **HTTPS**: Use TLS certificates in production

## Scalability Notes

### Current Limitations
- No persistent database (meals reset daily)
- Single OpenAI API key (rate limits apply)
- Local iOS storage only
- No multi-device sync

### Future Enhancements
1. **Database**: PostgreSQL for meal history
2. **Caching**: Redis for budget calculations
3. **Queue**: Celery for async image processing
4. **CDN**: Store photos in S3/CloudFront
5. **Sync**: CloudKit or custom backend sync

## Performance

### Backend
- Budget calculation: <10ms (deterministic)
- Image analysis: 2-5s (GPT-4o vision)
- Text generation: 1-3s (GPT-4o-mini)
- Total meal analysis: ~5-10s

### iOS
- Camera capture: Instant
- Image upload: 0.5-2s (depends on network)
- UI rendering: <100ms
- Total user flow: ~10-15s from snap to results

## Testing Strategy

### Backend Testing
```bash
# Unit tests
pytest backend/tests/test_nutrition.py
pytest backend/tests/test_models.py

# Integration tests
pytest backend/tests/test_api.py

# Manual testing
curl -X POST http://localhost:8000/budget -H "Content-Type: application/json" -d '{...}'
```

### iOS Testing
- Unit tests for models & networking
- UI tests for registration flow
- Manual device testing for camera
- Simulator testing for logic

## Deployment

### Backend
```bash
# Production server
gunicorn backend.main:app -w 4 -k uvicorn.workers.UvicornWorker

# Docker
docker build -t heal-backend .
docker run -e OPENAI_API_KEY=$OPENAI_API_KEY -p 8000:8000 heal-backend
```

### iOS
- Archive in Xcode
- Upload to App Store Connect
- TestFlight beta testing
- App Store release

## Monitoring

### Recommended Tools
- **Backend**: Sentry for errors, DataDog for metrics
- **iOS**: Firebase Crashlytics, Analytics
- **API**: OpenAI usage dashboard for token tracking
- **Uptime**: UptimeRobot or Pingdom

## Cost Estimation

### OpenAI API Costs (per user/day)
- Registration: 1 call × $0.001 = $0.001
- Meal analysis: 3 meals × ($0.02 image + $0.005 text × 2) = $0.09
- Daily summary: 1 × $0.005 = $0.005
- **Total: ~$0.10/user/day**

### Infrastructure (AWS example)
- EC2 t3.small: $15/month
- S3 storage: $1/month (1000 users)
- RDS PostgreSQL: $20/month
- **Total: ~$36/month base + $3/1000 active users**

---

## Development Roadmap

### Phase 1: MVP (Current)
- ✅ Basic registration
- ✅ Photo-based meal tracking
- ✅ Real-time feedback
- ✅ Daily summaries

### Phase 2: Core Features
- [ ] Persistent meal history
- [ ] User authentication
- [ ] Meal reminders/notifications
- [ ] Weekly trend charts

### Phase 3: Advanced
- [ ] Apple Health integration
- [ ] Barcode scanning
- [ ] Recipe suggestions
- [ ] Social features (share progress)

### Phase 4: Professional
- [ ] Healthcare provider portal
- [ ] Blood glucose integration
- [ ] Insulin dosing suggestions (requires medical review)
- [ ] HIPAA compliance

