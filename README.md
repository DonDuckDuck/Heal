# Heal - Diabetes Nutrition Assistant

Unhealthy eating habits are a major cause of type 2 diabetes and related diseases. Using data from the CGMacros dataset from 45 participants，— we explored how food composition affects blood glucose levels.
the CGMacros dataset, records 10 days of meals and continuous glucose readings from healthy, prediabetic, and diabetic participants, we found clear differences in eating patterns. Diabetic individuals tend to consume more carbohydrates and protein per meal, and their blood glucose remains higher across all carb intake levels. These results show that meal composition—not just calories—has a strong impact on glucose control.
<img width="1309" height="768" alt="图片_2025-10-26_115553_090" src="https://github.com/user-attachments/assets/bdd7f378-f107-4255-9997-69e88e2985c0" /><img width="1309" height="768" alt="图片_2025-10-26_115553_090" src="https://github.com/user-attachments/assets/a69bd0df-ca66-4255-8443-bffa88e23e7b" />


To address this, we developed Heal, an AI-powered nutrition assistant for diabetes management. Users can simply take a photo of their meal to get instant estimates of calories, carbs, protein, and fat, along with real-time feedback and personalized suggestions. Heal helps people with diabetes understand how their daily food choices affect blood sugar and make healthier eating decisions with ease.

## Features

- **AI-Powered Profile Generation**: Generate personalized calorie and macro budgets based on height, weight, age, sex, exercise level, and diabetes type (T1D/T2D)
- **Photo-Based Meal Tracking**: Snap a photo to automatically calculate calories, protein, carbs, and fat
- **Real-Time Feedback**: Get instant comparisons against per-meal and daily targets
- **Actionable Suggestions**: Receive immediate, implementable advice on portion adjustments and food swaps
- **Daily Summaries**: End-of-day analysis with next-day focus points
- **Progress Tracking**: Visual progress bars and meal history

## Architecture

### Backend (FastAPI)
```
backend/
├── main.py          # FastAPI app and route definitions
├── models.py        # Pydantic request/response models
├── schemas.py       # OpenAI JSON schemas for structured outputs
├── llm.py           # LLM service layer (all OpenAI calls)
├── nutrition.py     # Deterministic nutrition calculations
└── routes.py        # API route handlers
```

### iOS App (SwiftUI)

**Source files are in `HealAPP/` directory:**
```
HealAPP/
├── HealApp.swift                    # App entry point
├── Models/
│   ├── AppState.swift              # Global app state
│   └── DataModels.swift            # Data structures
├── Services/
│   └── APIService.swift            # Backend API client
└── Views/
    ├── RegistrationView.swift      # User onboarding
    ├── MainTabView.swift           # Tab navigation
    ├── CameraView.swift            # Camera & meal analysis
    ├── TodayView.swift             # Daily progress
    ├── ProgressView.swift          # Weekly trends (placeholder)
    └── ProfileView.swift           # User profile
```

**Note**: The `ios/` directory contains Xcode project files. To create your own Xcode project, see instructions below.

## Setup

### Backend

1. **Install dependencies**
```bash
cd /path/to/Heal
pip install -r requirements.txt
```

2. **Set environment variable**
```bash
export OPENAI_API_KEY="your-openai-api-key"
```

3. **Run the server**
```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### iOS App

#### Creating the Xcode Project

1. **Open Xcode** and create a new iOS App project:
   - File → New → Project
   - Choose iOS → App
   - Product Name: `Heal`
   - Interface: **SwiftUI** (important!)
   - Save location: Desktop or Documents (not in the `ios/` folder)

2. **Delete template files**:
   - Delete `ContentView.swift`
   - Delete the default `HealApp.swift`

3. **Add source files**:
   - Open `HealAPP/` folder in Finder
   - Select all files (HealApp.swift, Models/, Services/, Views/)
   - Drag into Xcode project
   - Check "Copy items if needed" and add to target

4. **Configure camera permissions**:
   - Project settings → Info tab
   - Add: `Privacy - Camera Usage Description`
   - Value: `Heal needs camera access to analyze your meals`

5. **Update API URL**:
   - Open `Services/APIService.swift`
   - Line 13: Update `baseURL`
     - Simulator: `http://localhost:8000`
     - Device: `http://YOUR_IP:8000` (get with `ipconfig getifaddr en0`)

6. **Build and run** (Cmd+R) on simulator or device (iOS 15.0+)

## API Endpoints

### `POST /budget`
Calculate daily calorie and macro budget
```json
{
  "height_cm": 170,
  "weight_kg": 70,
  "age": 30,
  "sex": "male",
  "exercise_level": "moderate",
  "diabetes_type": "T2D",
  "meals_per_day": 3
}
```

### `POST /estimate`
Upload food photo for nutrition analysis (multipart/form-data with `image` field)

### `POST /llm/compare`
Compare current meal against targets

### `POST /llm/suggestions`
Get actionable meal suggestions

### `POST /llm/daily_summary`
Generate end-of-day summary and next-day focus

### `GET /health`
Health check endpoint

## Usage Flow

1. **Registration**: User enters health info → Backend calculates personalized daily and per-meal targets
2. **Meal Time**: User takes photo → AI analyzes nutrition → Compares to targets → Provides suggestions
3. **Save Meal**: User confirms → App updates progress bars and daily totals
4. **End of Day**: App generates summary with actionable next-day recommendations

## Tech Stack

- **Backend**: FastAPI, OpenAI GPT-4o/4o-mini, Pydantic, Pillow
- **iOS**: SwiftUI, Combine, URLSession
- **AI Models**: 
  - GPT-4o for image analysis
  - GPT-4o-mini for text generation (comparisons, suggestions, summaries)

## Development

### Running Tests
```bash
# Backend (add tests in backend/tests/)
pytest

# iOS (add tests in Xcode)
```

### Backend Development
```bash
# Hot reload enabled by default
uvicorn backend.main:app --reload
```

### iOS Development
- Use Xcode simulator for rapid iteration
- Test on real device for camera functionality
- Update `baseURL` in `APIService.swift` when switching between local/remote

## Environment Variables

- `OPENAI_API_KEY` (required): Your OpenAI API key

## Notes

- The app currently uses local state (UserDefaults for profile, in-memory for meals)
- For production, add persistent storage (Core Data, CloudKit, or backend database)
- Meal reminders require local notifications (add `UNUserNotificationCenter` integration)
- Daily summary trigger can use background tasks or scheduled notifications

## License

LGPL

## Support

For issues or questions, please open an issue on GitHub.

