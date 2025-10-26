//
//  RegistrationView.swift
//  Heal
//

import SwiftUI

struct RegistrationView: View {
    @EnvironmentObject var appState: AppState
    @State private var heightCm: String = ""
    @State private var weightKg: String = ""
    @State private var age: String = ""
    @State private var sex: String = "male"
    @State private var exerciseLevel: String = "moderate"
    @State private var diabetesType: String = "T2D"
    @State private var mealsPerDay: Int = 3
    @State private var isLoading = false
    @State private var errorMessage: String?
    
    let sexOptions = ["male", "female"]
    let exerciseOptions = ["sedentary", "light", "moderate", "active", "very_active"]
    let diabetesOptions = ["T1D", "T2D", "unknown"]
    
    var body: some View {
        NavigationView {
            Form {
                Section(header: Text("Basic Information")) {
                    HStack {
                        Text("Height (cm)")
                        Spacer()
                        TextField("170", text: $heightCm)
                            .keyboardType(.decimalPad)
                            .multilineTextAlignment(.trailing)
                    }
                    
                    HStack {
                        Text("Weight (kg)")
                        Spacer()
                        TextField("70", text: $weightKg)
                            .keyboardType(.decimalPad)
                            .multilineTextAlignment(.trailing)
                    }
                    
                    HStack {
                        Text("Age")
                        Spacer()
                        TextField("30", text: $age)
                            .keyboardType(.numberPad)
                            .multilineTextAlignment(.trailing)
                    }
                    
                    Picker("Sex", selection: $sex) {
                        ForEach(sexOptions, id: \.self) { option in
                            Text(option.capitalized).tag(option)
                        }
                    }
                }
                
                Section(header: Text("Activity & Health")) {
                    Picker("Exercise Level", selection: $exerciseLevel) {
                        ForEach(exerciseOptions, id: \.self) { option in
                            Text(option.replacingOccurrences(of: "_", with: " ").capitalized).tag(option)
                        }
                    }
                    
                    Picker("Diabetes Type", selection: $diabetesType) {
                        ForEach(diabetesOptions, id: \.self) { option in
                            Text(option).tag(option)
                        }
                    }
                }
                
                Section(header: Text("Meal Schedule")) {
                    Stepper("Meals per day: \(mealsPerDay)", value: $mealsPerDay, in: 1...8)
                }
                
                if let error = errorMessage {
                    Section {
                        Text(error)
                            .foregroundColor(.red)
                    }
                }
                
                Section {
                    Button(action: register) {
                        if isLoading {
                            ProgressView()
                                .frame(maxWidth: .infinity)
                        } else {
                            Text("Complete Registration")
                                .font(.body.bold())
                                .frame(maxWidth: .infinity)
                        }
                    }
                    .disabled(isLoading || !isValid)
                }
            }
            .navigationTitle("Welcome to Heal")
        }
    }
    
    var isValid: Bool {
        guard let h = Double(heightCm), h > 0,
              let w = Double(weightKg), w > 0,
              let a = Int(age), a >= 10, a <= 120 else {
            return false
        }
        return true
    }
    
    func register() {
        guard isValid else { return }
        
        let profile = UserProfile(
            heightCm: Double(heightCm)!,
            weightKg: Double(weightKg)!,
            age: Int(age)!,
            sex: sex,
            exerciseLevel: exerciseLevel,
            diabetesType: diabetesType,
            mealsPerDay: mealsPerDay,
            mealTimes: generateMealTimes(count: mealsPerDay)
        )
        
        isLoading = true
        errorMessage = nil
        
        Task {
            do {
                let budget = try await APIService.shared.calculateBudget(profile: profile)
                await MainActor.run {
                    appState.register(profile: profile, budget: budget)
                    isLoading = false
                }
            } catch {
                await MainActor.run {
                    errorMessage = "Failed to calculate budget: \(error.localizedDescription)"
                    isLoading = false
                }
            }
        }
    }
    
    func generateMealTimes(count: Int) -> [String] {
        let defaults = ["08:00", "12:00", "18:00", "21:00", "06:00", "15:00", "10:00", "16:00"]
        return Array(defaults.prefix(count))
    }
}

