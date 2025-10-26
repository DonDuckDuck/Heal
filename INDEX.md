# Heal - Project Index

Complete directory listing and file descriptions for the diabetes nutrition management app.

## 📁 Project Structure

```
Heal/
├── 📚 Documentation (7 files)
│   ├── README.md ..................... Full project documentation
│   ├── QUICKSTART.md ................. 5-minute setup guide
│   ├── ARCHITECTURE.md ............... Technical deep dive
│   ├── PROJECT_SUMMARY.md ............ What we built & highlights
│   ├── INDEX.md ...................... This file
│   ├── ios/README.md ................. iOS-specific setup
│   └── .gitignore .................... Git ignore rules
│
├── 🐍 Backend (Python/FastAPI - 8 files)
│   ├── app.py ........................ DEPRECATED - backward compat wrapper
│   ├── backend/
│   │   ├── __init__.py ............... Package initialization
│   │   ├── main.py ................... FastAPI app & route definitions
│   │   ├── models.py ................. Pydantic request/response models
│   │   ├── schemas.py ................ OpenAI JSON schemas
│   │   ├── llm.py .................... OpenAI API service layer
│   │   ├── nutrition.py .............. BMR/TDEE/macro calculations
│   │   └── routes.py ................. API route handlers
│   ├── requirements.txt .............. Python dependencies
│   ├── start_server.sh ............... Quick start script
│   └── test_backend.py ............... Backend test suite
│
└── 📱 iOS App (SwiftUI - 13 files)
    └── ios/
        ├── Heal.xcodeproj/
        │   └── project.pbxproj ........ Xcode project (create manually)
        └── Heal/
            ├── HealApp.swift .......... App entry point
            ├── Info.plist ............. App permissions & config
            ├── Models/
            │   ├── AppState.swift ..... Global state management
            │   └── DataModels.swift ... Data structures (20+ types)
            ├── Services/
            │   └── APIService.swift ... Backend API client
            └── Views/
                ├── RegistrationView.swift ... User onboarding
                ├── MainTabView.swift ........ Tab navigation
                ├── CameraView.swift ......... Photo capture & analysis
                ├── TodayView.swift .......... Daily progress
                ├── ProgressView.swift ....... Weekly trends (placeholder)
                └── ProfileView.swift ........ User profile
```

## 📖 File Descriptions

### Documentation Files

#### `README.md` (Main Documentation)
- Complete project overview
- Setup instructions (backend + iOS)
- API endpoint documentation
- Architecture overview
- Development & deployment guides

#### `QUICKSTART.md` (Setup Guide)
- 5-minute backend setup
- 10-minute iOS setup
- Testing instructions
- Troubleshooting common issues

#### `ARCHITECTURE.md` (Technical Details)
- System architecture diagrams
- Data flow examples
- Component descriptions
- AI model usage
- Performance & scalability notes
- Security considerations

#### `PROJECT_SUMMARY.md` (Overview)
- What we built
- Key features breakdown
- Technology stack
- User flow diagrams
- Code highlights
- Success metrics

### Backend Files

#### `backend/main.py` (Entry Point)
**Purpose**: FastAPI application initialization
- Creates FastAPI app instance
- Configures CORS middleware
- Registers all API routes
- Health check endpoint
**Lines**: ~80

#### `backend/models.py` (Data Models)
**Purpose**: Pydantic models for validation
- `Macros`: Protein/carb/fat/kcal structure
- `BudgetRequest`: Registration form data
- `CompareMealRequest`: Meal comparison input
- `SuggestionsRequest`: Suggestion input
- `CopyRequest`: Notification copy input
- `DailySummaryRequest`: Summary input
**Lines**: ~70

#### `backend/schemas.py` (JSON Schemas)
**Purpose**: OpenAI structured output schemas
- `food_estimate_schema()`: Food analysis structure
- `meal_compare_schema()`: Comparison output format
- `suggestions_schema()`: Suggestion format
- `reminder_copy_schema()`: Notification copy format
- `daily_summary_schema()`: Summary format
**Lines**: ~400

#### `backend/llm.py` (LLM Service)
**Purpose**: All OpenAI API interactions
- `img_to_data_uri()`: Image preprocessing
- `estimate_food_from_image()`: GPT-4o vision analysis
- `compare_meal_to_targets()`: GPT-4o-mini comparison
- `generate_meal_suggestions()`: GPT-4o-mini suggestions
- `generate_reminder_copy()`: GPT-4o-mini notifications
- `generate_daily_summary()`: GPT-4o-mini summaries
**Lines**: ~170

#### `backend/nutrition.py` (Calculations)
**Purpose**: Deterministic nutrition math
- `activity_factor()`: Exercise level → multiplier
- `macro_split()`: Diabetes-optimized percentages
- `calculate_budget()`: Mifflin-St Jeor BMR → TDEE → macros
**Lines**: ~60

#### `backend/routes.py` (Route Handlers)
**Purpose**: API endpoint implementations
- `estimate_meal()`: Handle image upload
- `calc_budget_endpoint()`: Calculate budget
- `compare_meal_endpoint()`: Compare meal
- `suggestions_endpoint()`: Generate suggestions
- `copy_endpoint()`: Generate copy
- `daily_summary_endpoint()`: Generate summary
**Lines**: ~90

#### `app.py` (Deprecated)
**Purpose**: Backward compatibility
- Imports new modular backend
- Prints deprecation warning
- Allows old command to work
**Lines**: ~30

#### `requirements.txt` (Dependencies)
```
fastapi
uvicorn[standard]
python-multipart
pydantic>=2
openai>=1.40
Pillow
```

#### `start_server.sh` (Launch Script)
**Purpose**: One-command server startup
- Checks for OPENAI_API_KEY
- Creates venv if needed
- Installs dependencies
- Starts uvicorn server

#### `test_backend.py` (Test Suite)
**Purpose**: Verify backend functionality
- Tests all endpoints
- Uses sample images from project
- Displays results
- Helpful for debugging

### iOS Files

#### `ios/Heal/HealApp.swift` (Entry Point)
**Purpose**: SwiftUI app entry
- Defines app lifecycle
- Creates AppState
- Routes to Registration or Main view
**Lines**: ~20

#### `ios/Heal/Models/AppState.swift` (State)
**Purpose**: Global app state management
- `@Published` properties for reactive UI
- User profile & budget storage
- Today's meals tracking
- Daily consumed macros
- UserDefaults persistence
**Lines**: ~70

#### `ios/Heal/Models/DataModels.swift` (Types)
**Purpose**: All data structures
**Structs** (20+ types):
- `UserProfile`, `Macros`, `DailyBudget`
- `FoodEstimate`, `FoodItem`, `CalorieRange`
- `MealRecord`, `MealComparison`
- `MacroEvaluation`, `DailyEvaluation`
- `ComparisonFlags`, `ProgressBars`
- `MealSuggestions`, `Action`
- `DailySummary`, `MacroOverview`
**Lines**: ~250

#### `ios/Heal/Services/APIService.swift` (Networking)
**Purpose**: Backend communication
- `calculateBudget()`: POST /budget
- `estimateMeal()`: POST /estimate (multipart)
- `compareMeal()`: POST /llm/compare
- `getSuggestions()`: POST /llm/suggestions
- `getDailySummary()`: POST /llm/daily_summary
- Helper: `macrosToDict()`
**Lines**: ~200

#### `ios/Heal/Views/RegistrationView.swift` (Onboarding)
**Purpose**: User registration form
- Input fields for height, weight, age, sex
- Pickers for exercise, diabetes type
- Stepper for meals per day
- Validation & API call
- Saves profile & budget
**Lines**: ~120

#### `ios/Heal/Views/MainTabView.swift` (Navigation)
**Purpose**: Tab bar container
- 4 tabs: Today, Camera, Progress, Profile
- Passes AppState to all views
**Lines**: ~30

#### `ios/Heal/Views/CameraView.swift` (Core Feature)
**Purpose**: Photo capture & analysis
- Camera integration (ImagePicker)
- Image upload & analysis
- Display nutrition estimate
- Show comparison & suggestions
- Save or retake flow
**Sub-views**:
- `ResultView`: Display analysis
- `MacroCard`: Macro display
- `ComparisonCard`: Target comparison
- `SuggestionsCard`: Actionable tips
- `ImagePicker`: UIKit camera wrapper
**Lines**: ~350

#### `ios/Heal/Views/TodayView.swift` (Progress)
**Purpose**: Daily overview
- Daily progress bars (protein/carb/fat)
- List of today's meals
- Visual feedback on targets
**Sub-views**:
- `DailyProgressCard`: Overall progress
- `ProgressBar`: Individual macro bar
- `MealCard`: Single meal summary
**Lines**: ~150

#### `ios/Heal/Views/ProfileView.swift` (Settings)
**Purpose**: User information display
- Personal info (height, weight, age, sex)
- Health info (diabetes type, exercise)
- Daily budget breakdown
**Lines**: ~70

#### `ios/Heal/Views/ProgressView.swift` (Trends)
**Purpose**: Weekly/monthly trends
- Currently placeholder
- Future: Charts & insights
**Lines**: ~20

#### `ios/Heal/Info.plist` (Configuration)
**Purpose**: App permissions & metadata
- Camera usage description
- Photo library usage description
- Scene manifest for SwiftUI
**Lines**: ~15

## 📊 Statistics

### Code Count
- **Backend Python**: ~900 lines
- **iOS Swift**: ~1,300 lines
- **Documentation**: ~1,200 lines
- **Config/Scripts**: ~100 lines
- **Total**: ~3,500 lines

### File Count
- **Backend**: 10 files
- **iOS**: 13 files
- **Documentation**: 7 files
- **Total**: 30 files

### API Endpoints
- `GET /health` - Health check
- `POST /budget` - Calculate macro budget
- `POST /estimate` - Analyze food photo
- `POST /llm/compare` - Compare to targets
- `POST /llm/suggestions` - Generate tips
- `POST /llm/daily_summary` - Daily insights
- **Total**: 6 endpoints

### Data Models
- **Backend (Pydantic)**: 6 request models
- **iOS (Swift)**: 20+ structs
- **JSON Schemas**: 5 structured outputs

## 🚀 Quick Navigation

### I want to...

**Understand the project**
→ Start with `PROJECT_SUMMARY.md`
→ Then read `README.md`

**Set up the backend**
→ Follow `QUICKSTART.md` backend section
→ Run `./start_server.sh`

**Set up iOS app**
→ Follow `QUICKSTART.md` iOS section
→ See `ios/README.md` for details

**Understand the architecture**
→ Read `ARCHITECTURE.md`
→ Check diagrams and data flows

**Modify nutrition calculations**
→ Edit `backend/nutrition.py`
→ Test with `test_backend.py`

**Change AI prompts**
→ Edit `backend/llm.py`
→ Modify system prompts
→ Adjust temperature/timeout

**Update iOS UI**
→ Edit files in `ios/Heal/Views/`
→ `CameraView.swift` for main flow
→ `TodayView.swift` for progress

**Add new API endpoint**
→ Define schema in `backend/schemas.py`
→ Add model in `backend/models.py`
→ Create handler in `backend/routes.py`
→ Register in `backend/main.py`
→ Add client method in `ios/Heal/Services/APIService.swift`

**Debug issues**
→ Backend: Check FastAPI docs at `/docs`
→ Backend: Run `test_backend.py`
→ iOS: Check Xcode console logs
→ iOS: Add `print()` statements

## 📝 Key Concepts

### Backend Patterns
- **Separation of concerns**: Routes → Handlers → Services → Utilities
- **Type safety**: Pydantic validation on all inputs
- **Structured outputs**: JSON schemas for reliable parsing
- **Modular design**: Each file has single responsibility

### iOS Patterns
- **MVVM-ish**: Views + AppState + APIService
- **SwiftUI**: Declarative, reactive UI
- **Combine**: @Published for state changes
- **URLSession**: Async/await networking

### AI Integration
- **GPT-4o**: Image analysis (high accuracy, slower)
- **GPT-4o-mini**: Text generation (fast, cheap)
- **Structured outputs**: No parsing, no errors
- **Temperature tuning**: 0 for deterministic, 0.2-0.5 for creative

## 🎯 Next Steps

1. **Run the backend**: `./start_server.sh`
2. **Test the API**: `python test_backend.py`
3. **Build iOS app**: Follow `ios/README.md`
4. **Try the flow**: Register → Photo → Review → Save
5. **Read docs**: Explore `ARCHITECTURE.md` for deep dive

## 📞 Support

- **Issues**: Check `QUICKSTART.md` troubleshooting
- **Architecture questions**: See `ARCHITECTURE.md`
- **API reference**: Visit `http://localhost:8000/docs` when server is running
- **iOS setup**: Read `ios/README.md`

---

**Happy building! 🏥💚**

