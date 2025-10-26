//
//  TodayView.swift
//  Heal
//

import SwiftUI

struct TodayView: View {
    @EnvironmentObject var appState: AppState
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 20) {
                    if let budget = appState.dailyBudget {
                        DailyProgressCard(
                            consumed: appState.dailyConsumed,
                            target: budget.dailyBudget
                        )
                    }
                    
                    VStack(alignment: .leading, spacing: 12) {
                        Text("Meals Today")
                            .font(.headline)
                            .padding(.horizontal)
                        
                        if appState.todayMeals.isEmpty {
                            Text("No meals logged yet")
                                .foregroundColor(.secondary)
                                .frame(maxWidth: .infinity, alignment: .center)
                                .padding()
                        } else {
                            ForEach(appState.todayMeals) { meal in
                                MealCard(meal: meal)
                            }
                        }
                    }
                }
                .padding()
            }
            .navigationTitle("Today")
        }
    }
}

struct DailyProgressCard: View {
    let consumed: Macros
    let target: Macros
    
    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Daily Progress")
                .font(.headline)
            
            ProgressBar(label: "Protein", current: consumed.proteinG, target: target.proteinG, color: .blue)
            ProgressBar(label: "Carbs", current: consumed.carbG, target: target.carbG, color: .orange)
            ProgressBar(label: "Fat", current: consumed.fatG, target: target.fatG, color: .purple)
            
            HStack {
                Text("Calories")
                    .font(.subheadline)
                Spacer()
                Text("\(Int(consumed.kcal)) / \(Int(target.kcal)) kcal")
                    .font(.subheadline.bold())
            }
        }
        .padding()
        .background(Color(.systemGray6))
        .cornerRadius(12)
    }
}

struct ProgressBar: View {
    let label: String
    let current: Double
    let target: Double
    let color: Color
    
    var progress: Double {
        min(current / target, 1.0)
    }
    
    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            HStack {
                Text(label)
                    .font(.subheadline)
                Spacer()
                Text("\(Int(current))g / \(Int(target))g")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            
            GeometryReader { geometry in
                ZStack(alignment: .leading) {
                    Rectangle()
                        .fill(Color.gray.opacity(0.2))
                        .frame(height: 8)
                        .cornerRadius(4)
                    
                    Rectangle()
                        .fill(current > target ? Color.red : color)
                        .frame(width: geometry.size.width * CGFloat(progress), height: 8)
                        .cornerRadius(4)
                }
            }
            .frame(height: 8)
        }
    }
}

struct MealCard: View {
    let meal: MealRecord
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Text(meal.mealName)
                    .font(.headline)
                Spacer()
                Text(meal.timestamp, style: .time)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            
            HStack {
                Label("\(Int(meal.macros.proteinG))g", systemImage: "p.circle.fill")
                    .foregroundColor(.blue)
                Label("\(Int(meal.macros.carbG))g", systemImage: "c.circle.fill")
                    .foregroundColor(.orange)
                Label("\(Int(meal.macros.fatG))g", systemImage: "f.circle.fill")
                    .foregroundColor(.purple)
                Spacer()
                Text("\(Int(meal.macros.kcal)) kcal")
                    .font(.caption.bold())
            }
            .font(.caption)
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(8)
        .overlay(
            RoundedRectangle(cornerRadius: 8)
                .stroke(Color(.separator), lineWidth: 1)
        )
        .shadow(color: Color.black.opacity(0.1), radius: 2)
        .padding(.horizontal)
    }
}

