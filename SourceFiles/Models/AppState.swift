//
//  AppState.swift
//  Heal
//

import Foundation
import SwiftUI
import Combine

class AppState: ObservableObject {
    @Published var isRegistered: Bool = false
    @Published var userProfile: UserProfile?
    @Published var dailyBudget: DailyBudget?
    @Published var todayMeals: [MealRecord] = []
    @Published var dailyConsumed: Macros = Macros(proteinG: 0, fatG: 0, carbG: 0, kcal: 0)
    
    init() {
        loadUserProfile()
    }
    
    func register(profile: UserProfile, budget: DailyBudget) {
        self.userProfile = profile
        self.dailyBudget = budget
        self.isRegistered = true
        saveUserProfile()
    }
    
    func addMeal(_ meal: MealRecord) {
        todayMeals.append(meal)
        updateDailyConsumed()
    }
    
    func updateDailyConsumed() {
        dailyConsumed = todayMeals.reduce(Macros(proteinG: 0, fatG: 0, carbG: 0, kcal: 0)) { acc, meal in
            Macros(
                proteinG: acc.proteinG + meal.macros.proteinG,
                fatG: acc.fatG + meal.macros.fatG,
                carbG: acc.carbG + meal.macros.carbG,
                kcal: acc.kcal + meal.macros.kcal
            )
        }
    }
    
    func resetDay() {
        todayMeals = []
        dailyConsumed = Macros(proteinG: 0, fatG: 0, carbG: 0, kcal: 0)
    }
    
    private func saveUserProfile() {
        if let profile = userProfile, let budget = dailyBudget {
            if let encoded = try? JSONEncoder().encode(profile) {
                UserDefaults.standard.set(encoded, forKey: "userProfile")
            }
            if let encoded = try? JSONEncoder().encode(budget) {
                UserDefaults.standard.set(encoded, forKey: "dailyBudget")
            }
        }
    }
    
    private func loadUserProfile() {
        if let data = UserDefaults.standard.data(forKey: "userProfile"),
           let profile = try? JSONDecoder().decode(UserProfile.self, from: data),
           let budgetData = UserDefaults.standard.data(forKey: "dailyBudget"),
           let budget = try? JSONDecoder().decode(DailyBudget.self, from: budgetData) {
            self.userProfile = profile
            self.dailyBudget = budget
            self.isRegistered = true
        }
    }
}

