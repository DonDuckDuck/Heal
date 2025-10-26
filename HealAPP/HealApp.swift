//
//  HealApp.swift
//  Heal - Diabetes Nutrition Assistant
//

import SwiftUI

@main
struct HealApp: App {
    @StateObject private var appState = AppState()
    
    var body: some Scene {
        WindowGroup {
            if appState.isRegistered {
                MainTabView()
                    .environmentObject(appState)
            } else {
                RegistrationView()
                    .environmentObject(appState)
            }
        }
    }
}

