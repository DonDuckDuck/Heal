//
//  CameraView.swift
//  Heal
//

import SwiftUI
import UIKit

struct CameraView: View {
    @EnvironmentObject var appState: AppState
    @State private var showCamera = false
    @State private var capturedImage: UIImage?
    @State private var isAnalyzing = false
    @State private var estimate: FoodEstimate?
    @State private var comparison: MealComparison?
    @State private var suggestions: MealSuggestions?
    @State private var errorMessage: String?
    
    var body: some View {
        NavigationView {
            ZStack {
                if let image = capturedImage {
                    // Scrollable content for analysis results
                    ScrollView {
                        VStack(spacing: 0) {
                            // Image header with aspect ratio preservation
                            Image(uiImage: image)
                                .resizable()
                                .scaledToFill()
                                .frame(height: 250)
                                .clipped()
                                .cornerRadius(0)
                            
                            // Content below image
                            VStack(spacing: 16) {
                                if isAnalyzing {
                                    ProgressView("Analyzing your meal...")
                                        .padding(.top, 32)
                                } else if let estimate = estimate {
                                    ResultView(
                                        estimate: estimate,
                                        comparison: comparison,
                                        suggestions: suggestions,
                                        onSave: saveMeal,
                                        onRetake: retakePicture
                                    )
                                    .padding(.top, 16)
                                }
                                
                                if let error = errorMessage {
                                    Text(error)
                                        .foregroundColor(.red)
                                        .padding()
                                }
                            }
                        }
                    }
                    .navigationTitle("Analysis")
                    .navigationBarTitleDisplayMode(.inline)
                } else {
                    // Empty state (centered, no scroll)
                    VStack(spacing: 20) {
                        Spacer()
                        
                        Image(systemName: "camera.fill")
                            .font(.system(size: 80))
                            .foregroundColor(.blue)
                        
                        Text("Snap Your Meal")
                            .font(.title.bold())
                        
                        Text("Take a photo to analyze nutrition")
                            .foregroundColor(.secondary)
                        
                        Button(action: { showCamera = true }) {
                            Text("Open Camera")
                                .font(.body.bold())
                                .frame(maxWidth: .infinity)
                                .padding()
                                .background(Color.blue)
                                .foregroundColor(.white)
                                .cornerRadius(12)
                        }
                        .padding(.horizontal, 40)
                        
                        Spacer()
                    }
                    .navigationTitle("Meal Tracker")
                    .navigationBarTitleDisplayMode(.large)
                }
            }
            .fullScreenCover(isPresented: $showCamera) {
                ImagePicker(image: $capturedImage, onImagePicked: analyzeMeal)
                    .edgesIgnoringSafeArea(.all)
            }
        }
    }
    
    func analyzeMeal() {
        guard let image = capturedImage else { return }
        
        isAnalyzing = true
        errorMessage = nil
        
        Task {
            do {
                let est = try await APIService.shared.estimateMeal(image: image)
                
                let mealIndex = appState.todayMeals.count + 1
                let comp = try await APIService.shared.compareMeal(
                    perMealTargets: appState.dailyBudget!.perMealTargets,
                    dailyTargets: appState.dailyBudget!.dailyBudget,
                    dailyConsumedSoFar: appState.dailyConsumed,
                    currentMeal: est.totals,
                    mealIndex: mealIndex,
                    mealsPerDay: appState.userProfile!.mealsPerDay,
                    mealName: getMealName(index: mealIndex),
                    diabetesType: appState.userProfile!.diabetesType
                )
                
                let remaining = calculateRemaining()
                let sugg = try await APIService.shared.getSuggestions(
                    estimate: est,
                    perMealTargets: appState.dailyBudget!.perMealTargets,
                    dailyRemaining: remaining,
                    mealName: getMealName(index: mealIndex),
                    diabetesType: appState.userProfile!.diabetesType
                )
                
                await MainActor.run {
                    estimate = est
                    comparison = comp
                    suggestions = sugg
                    isAnalyzing = false
                }
            } catch {
                await MainActor.run {
                    errorMessage = "Analysis failed: \(error.localizedDescription)"
                    isAnalyzing = false
                }
            }
        }
    }
    
    func saveMeal() {
        guard let estimate = estimate,
              let imageData = capturedImage?.jpegData(compressionQuality: 0.7) else {
            return
        }
        
        let mealIndex = appState.todayMeals.count + 1
        let meal = MealRecord(
            timestamp: Date(),
            mealIndex: mealIndex,
            mealName: getMealName(index: mealIndex),
            estimate: estimate,
            macros: estimate.totals,
            imageData: imageData
        )
        
        appState.addMeal(meal)
        
        capturedImage = nil
        self.estimate = nil
        comparison = nil
        suggestions = nil
    }
    
    func retakePicture() {
        capturedImage = nil
        estimate = nil
        comparison = nil
        suggestions = nil
        showCamera = true
    }
    
    func getMealName(index: Int) -> String {
        let names = ["Breakfast", "Lunch", "Dinner", "Snack"]
        return index <= names.count ? names[index - 1] : "Meal \(index)"
    }
    
    func calculateRemaining() -> Macros {
        guard let budget = appState.dailyBudget else {
            return Macros(proteinG: 0, fatG: 0, carbG: 0, kcal: 0)
        }
        
        return Macros(
            proteinG: max(0, budget.dailyBudget.proteinG - appState.dailyConsumed.proteinG),
            fatG: max(0, budget.dailyBudget.fatG - appState.dailyConsumed.fatG),
            carbG: max(0, budget.dailyBudget.carbG - appState.dailyConsumed.carbG),
            kcal: max(0, budget.dailyBudget.kcal - appState.dailyConsumed.kcal)
        )
    }
}

struct ResultView: View {
    let estimate: FoodEstimate
    let comparison: MealComparison?
    let suggestions: MealSuggestions?
    let onSave: () -> Void
    let onRetake: () -> Void
    
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                VStack(alignment: .leading, spacing: 8) {
                    Text("Nutrition Summary")
                        .font(.headline)
                    
                    HStack {
                        MacroCard(label: "Protein", value: estimate.totals.proteinG, unit: "g", color: .blue)
                        MacroCard(label: "Carbs", value: estimate.totals.carbG, unit: "g", color: .orange)
                        MacroCard(label: "Fat", value: estimate.totals.fatG, unit: "g", color: .purple)
                    }
                    
                    Text("\(Int(estimate.totals.kcal)) kcal")
                        .font(.title2.bold())
                }
                .padding()
                .background(Color(.systemGray6))
                .cornerRadius(12)
                
                if let comp = comparison {
                    ComparisonCard(comparison: comp)
                }
                
                if let sugg = suggestions {
                    SuggestionsCard(suggestions: sugg)
                }
                
                HStack(spacing: 12) {
                    Button(action: onRetake) {
                        Text("Retake")
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(Color(.systemGray5))
                            .foregroundColor(.primary)
                            .cornerRadius(12)
                    }
                    
                    Button(action: onSave) {
                        Text("Save Meal")
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(Color.green)
                            .foregroundColor(.white)
                            .cornerRadius(12)
                    }
                }
            }
            .padding()
        }
    }
}

struct MacroCard: View {
    let label: String
    let value: Double
    let unit: String
    let color: Color
    
    var body: some View {
        VStack {
            Text(label)
                .font(.caption)
                .foregroundColor(.secondary)
            Text("\(Int(value))\(unit)")
                .font(.headline)
                .foregroundColor(color)
        }
        .frame(maxWidth: .infinity)
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(8)
        .overlay(
            RoundedRectangle(cornerRadius: 8)
                .stroke(Color(.separator), lineWidth: 1)
        )
    }
}

struct ComparisonCard: View {
    let comparison: MealComparison
    
    func formatExceededItems(_ items: [String]) -> String {
        return items.map { item in
            switch item {
            case "protein_g": return "Protein"
            case "carb_g": return "Carbs"
            case "fat_g": return "Fat"
            default: return item.replacingOccurrences(of: "_g", with: "").capitalized
            }
        }.joined(separator: ", ")
    }
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Meal Analysis")
                .font(.headline)
            
            if comparison.flags.perMealExceededAny {
                HStack(alignment: .top, spacing: 8) {
                    Image(systemName: "exclamationmark.triangle.fill")
                        .foregroundColor(.orange)
                    VStack(alignment: .leading, spacing: 4) {
                        Text("Exceeded per-meal target:")
                            .font(.subheadline)
                            .foregroundColor(.orange)
                        Text(formatExceededItems(comparison.flags.overPerMeal))
                            .font(.subheadline)
                    }
                }
            }
            
            ForEach(comparison.notes, id: \.self) { note in
                Text("• \(note)")
                    .font(.subheadline)
                    .foregroundColor(.secondary)
            }
        }
        .padding()
        .background(Color(.systemGray6))
        .cornerRadius(12)
    }
}

struct SuggestionsCard: View {
    let suggestions: MealSuggestions
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("💡 Suggestions")
                .font(.headline)
            
            ForEach(suggestions.actions) { action in
                HStack(alignment: .top, spacing: 8) {
                    Text(actionIcon(action.kind))
                    Text(action.text)
                        .font(.subheadline)
                }
            }
        }
        .padding()
        .background(Color.blue.opacity(0.1))
        .cornerRadius(12)
    }
    
    func actionIcon(_ kind: String) -> String {
        switch kind {
        case "portion": return "🍽️"
        case "swap": return "🔄"
        case "add": return "➕"
        case "remove": return "➖"
        case "timing": return "⏰"
        case "order": return "📋"
        default: return "💡"
        }
    }
}

struct ImagePicker: UIViewControllerRepresentable {
    @Binding var image: UIImage?
    @Environment(\.dismiss) var dismiss
    let onImagePicked: () -> Void
    
    func makeUIViewController(context: Context) -> UIImagePickerController {
        let picker = UIImagePickerController()
        picker.sourceType = .camera
        picker.delegate = context.coordinator
        return picker
    }
    
    func updateUIViewController(_ uiViewController: UIImagePickerController, context: Context) {}
    
    func makeCoordinator() -> Coordinator {
        Coordinator(self)
    }
    
    class Coordinator: NSObject, UIImagePickerControllerDelegate, UINavigationControllerDelegate {
        let parent: ImagePicker
        
        init(_ parent: ImagePicker) {
            self.parent = parent
        }
        
        func imagePickerController(_ picker: UIImagePickerController, didFinishPickingMediaWithInfo info: [UIImagePickerController.InfoKey : Any]) {
            if let image = info[.originalImage] as? UIImage {
                parent.image = image
                parent.dismiss()
                parent.onImagePicked()
            }
        }
        
        func imagePickerControllerDidCancel(_ picker: UIImagePickerController) {
            parent.dismiss()
        }
    }
}

