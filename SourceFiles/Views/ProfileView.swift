//
//  ProfileView.swift
//  Heal
//

import SwiftUI

struct ProfileView: View {
    @EnvironmentObject var appState: AppState
    
    var body: some View {
        NavigationView {
            Form {
                if let profile = appState.userProfile {
                    Section(header: Text("Personal Info")) {
                        HStack {
                            Text("Height")
                            Spacer()
                            Text("\(Int(profile.heightCm)) cm")
                        }
                        HStack {
                            Text("Weight")
                            Spacer()
                            Text("\(Int(profile.weightKg)) kg")
                        }
                        HStack {
                            Text("Age")
                            Spacer()
                            Text("\(profile.age)")
                        }
                        HStack {
                            Text("Sex")
                            Spacer()
                            Text(profile.sex.capitalized)
                        }
                    }
                    
                    Section(header: Text("Health")) {
                        HStack {
                            Text("Diabetes Type")
                            Spacer()
                            Text(profile.diabetesType)
                        }
                        HStack {
                            Text("Exercise Level")
                            Spacer()
                            Text(profile.exerciseLevel.replacingOccurrences(of: "_", with: " ").capitalized)
                        }
                    }
                    
                    if let budget = appState.dailyBudget {
                        Section(header: Text("Daily Budget")) {
                            HStack {
                                Text("Calories")
                                Spacer()
                                Text("\(Int(budget.dailyBudget.kcal)) kcal")
                            }
                            HStack {
                                Text("Protein")
                                Spacer()
                                Text("\(Int(budget.dailyBudget.proteinG))g")
                            }
                            HStack {
                                Text("Carbs")
                                Spacer()
                                Text("\(Int(budget.dailyBudget.carbG))g")
                            }
                            HStack {
                                Text("Fat")
                                Spacer()
                                Text("\(Int(budget.dailyBudget.fatG))g")
                            }
                        }
                    }
                }
            }
            .navigationTitle("Profile")
        }
    }
}

