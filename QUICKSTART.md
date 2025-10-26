# Quick Start Guide

## Backend Setup (5 minutes)

1. **Set your OpenAI API key:**
```bash
export OPENAI_API_KEY="sk-your-api-key-here"
```

2. **Start the server:**
```bash
cd /path/to/Heal
./start_server.sh
```

Or manually:
```bash
# Create virtual environment (first time only)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start server
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

3. **Test the API:**
Open http://localhost:8000/docs in your browser

## iOS App Setup (10 minutes)

### Option 1: Using Xcode (Recommended)

1. **Open Xcode** and create new iOS App project:
   - File → New → Project → iOS → App
   - Name: `Heal`
   - Interface: SwiftUI
   - Language: Swift
   - Save to: `ios/` directory

2. **Add source files:**
   - Delete the default `ContentView.swift` and `HealApp.swift` from the template
   - Drag all `.swift` files from `ios/Heal/` into the Xcode project navigator
   - Check "Copy items if needed" and add to target

3. **Configure camera permissions:**
   - Select project in navigator → Info tab
   - Add key: `Privacy - Camera Usage Description`
   - Value: `Heal needs camera access to analyze meals`

4. **Update API URL:**
   - Open `Services/APIService.swift`
   - Update `baseURL`:
     - For simulator: `http://localhost:8000`
     - For device: `http://YOUR_IP:8000` (get with `ipconfig getifaddr en0`)

5. **Run:**
   - Connect iPhone or use simulator
   - Press Cmd+R to build and run

### Option 2: Command Line (Advanced)

```bash
cd ios
# Use xcodebuild if you have a working project file
xcodebuild -scheme Heal -destination 'platform=iOS Simulator,name=iPhone 14' build
```

## Testing the App

1. **Register** with your health info (height, weight, age, etc.)
2. **Take a photo** of food using the camera tab
3. **View analysis** with macro breakdown and suggestions
4. **Track progress** on the Today tab

## Architecture Overview

```
Heal/
├── backend/              # FastAPI server
│   ├── main.py          # App & routes
│   ├── llm.py           # OpenAI integration
│   ├── models.py        # Data models
│   ├── schemas.py       # JSON schemas
│   ├── nutrition.py     # Calorie calculations
│   └── routes.py        # Route handlers
│
└── ios/Heal/            # SwiftUI app
    ├── Models/          # Data structures
    ├── Services/        # API client
    └── Views/           # UI screens
```

## API Flow

1. **Registration** → `POST /budget` → Get daily macro targets
2. **Meal Photo** → `POST /estimate` → Analyze nutrition
3. **Compare** → `POST /llm/compare` → Check against targets
4. **Suggestions** → `POST /llm/suggestions` → Get actionable advice
5. **End of Day** → `POST /llm/daily_summary` → Generate summary

## Troubleshooting

### Backend Issues

**"ModuleNotFoundError"**
```bash
pip install -r requirements.txt
```

**"Set OPENAI_API_KEY"**
```bash
export OPENAI_API_KEY="your-key"
```

**Port 8000 already in use**
```bash
# Find and kill process
lsof -ti:8000 | xargs kill -9

# Or use different port
uvicorn backend.main:app --reload --port 8001
```

### iOS Issues

**Camera not working**
- Camera only works on physical devices, not simulator
- Check Info.plist has camera permission

**Cannot connect to backend**
- Simulator: Use `http://localhost:8000`
- Device: Use your computer's IP, not localhost
- Check firewall allows incoming connections on port 8000

**Build errors**
- Clean build folder: Cmd+Shift+K
- Delete DerivedData: `rm -rf ~/Library/Developer/Xcode/DerivedData`

## Next Steps

- Add persistent storage (Core Data or backend database)
- Implement meal time notifications
- Add weekly trend charts
- Integrate with Apple Health
- Add user authentication

## Support

See full documentation in `README.md`

