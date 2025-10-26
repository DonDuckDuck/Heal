# iOS App Setup

## Creating the Xcode Project

Since Xcode project files are binary and complex, please create the project manually:

1. **Open Xcode**
2. **File → New → Project**
3. **Choose iOS → App**
4. **Project settings:**
   - Product Name: `Heal`
   - Team: Your team
   - Organization Identifier: `com.yourcompany`
   - Interface: SwiftUI
   - Language: Swift
   - Minimum iOS: 15.0

5. **Save to:** `ios/` directory

6. **Add source files:**
   - Drag all `.swift` files from `ios/Heal/` into the Xcode project
   - Make sure "Copy items if needed" is checked
   - Add to target: Heal

7. **Configure Info.plist:**
   - The `Info.plist` file is already provided with camera permissions
   - Xcode 13+ uses Info.plist in the project, not a separate file
   - Add camera permission key in Project Settings → Info → Custom iOS Target Properties:
     - Key: `Privacy - Camera Usage Description`
     - Value: `Heal needs camera access to analyze your meals and provide nutrition insights`

8. **Update API URL:**
   - In `Services/APIService.swift`, change `baseURL`:
     - Simulator: `http://localhost:8000`
     - Device: `http://YOUR_COMPUTER_IP:8000` (find with `ifconfig` on Mac)

9. **Build and Run**
   - Cmd+R to build and run on simulator
   - For device testing, connect iPhone and select it as target

## Project Structure

```
Heal/
├── HealApp.swift               # App entry point
├── Models/
│   ├── AppState.swift         # Global state management
│   └── DataModels.swift       # Data structures
├── Services/
│   └── APIService.swift       # Backend API client
└── Views/
    ├── RegistrationView.swift # Onboarding
    ├── MainTabView.swift      # Tab navigation
    ├── CameraView.swift       # Camera & analysis
    ├── TodayView.swift        # Daily progress
    ├── ProgressView.swift     # Weekly trends
    └── ProfileView.swift      # User profile
```

## Running on Device

1. Connect your iPhone via USB
2. Trust the computer on your iPhone
3. In Xcode, select your device as the target
4. Update `baseURL` in `APIService.swift` to your computer's local IP
5. Cmd+R to build and run

## Troubleshooting

- **Camera not working in simulator**: Use a physical device
- **Cannot connect to backend**: Make sure firewall allows port 8000
- **Build errors**: Clean build folder (Cmd+Shift+K) and rebuild

