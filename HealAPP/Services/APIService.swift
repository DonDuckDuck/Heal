//
//  APIService.swift
//  Heal
//

import Foundation
import UIKit

class APIService {
    static let shared = APIService()
    
    private let baseURL = "http://localhost:8000"
    
    private init() {}
    
    func calculateBudget(profile: UserProfile) async throws -> DailyBudget {
        let url = URL(string: "\(baseURL)/budget")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let body: [String: Any] = [
            "height_cm": profile.heightCm,
            "weight_kg": profile.weightKg,
            "age": profile.age,
            "sex": profile.sex,
            "exercise_level": profile.exerciseLevel,
            "diabetes_type": profile.diabetesType,
            "meals_per_day": profile.mealsPerDay
        ]
        
        request.httpBody = try JSONSerialization.data(withJSONObject: body)
        
        let (data, _) = try await URLSession.shared.data(for: request)
        return try JSONDecoder().decode(DailyBudget.self, from: data)
    }
    
    func estimateMeal(image: UIImage) async throws -> FoodEstimate {
        guard let imageData = image.jpegData(compressionQuality: 0.8) else {
            throw APIError.invalidImage
        }
        
        let url = URL(string: "\(baseURL)/estimate")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        
        // Use simple boundary like curl does
        let boundary = "------------------------\(UUID().uuidString)"
        request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")
        
        var body = Data()
        
        // Mimicking curl's exact format
        let boundaryPrefix = "--\(boundary)\r\n"
        body.append(boundaryPrefix.data(using: .utf8)!)
        body.append("Content-Disposition: form-data; name=\"image\"; filename=\"photo.jpg\"\r\n".data(using: .utf8)!)
        body.append("Content-Type: image/jpeg\r\n\r\n".data(using: .utf8)!)
        body.append(imageData)
        body.append("\r\n".data(using: .utf8)!)
        body.append("--\(boundary)--\r\n".data(using: .utf8)!)
        
        request.httpBody = body
        
        print("📤 Uploading \(imageData.count) bytes to \(url)")
        print("   Boundary: \(boundary)")
        print("   Body size: \(body.count) bytes")
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        if let httpResponse = response as? HTTPURLResponse {
            print("📥 Status: \(httpResponse.statusCode)")
            if httpResponse.statusCode != 200 {
                let errorText = String(data: data, encoding: .utf8) ?? "Unknown error"
                print("❌ Error response: \(errorText)")
                throw APIError.networkError("Server returned \(httpResponse.statusCode): \(errorText)")
            }
        }
        
        return try JSONDecoder().decode(FoodEstimate.self, from: data)
    }
    
    func compareMeal(
        perMealTargets: Macros,
        dailyTargets: Macros,
        dailyConsumedSoFar: Macros,
        currentMeal: Macros,
        mealIndex: Int,
        mealsPerDay: Int,
        mealName: String?,
        diabetesType: String?
    ) async throws -> MealComparison {
        let url = URL(string: "\(baseURL)/llm/compare")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let body: [String: Any] = [
            "per_meal_targets": macrosToDict(perMealTargets),
            "daily_targets": macrosToDict(dailyTargets),
            "daily_consumed_so_far": macrosToDict(dailyConsumedSoFar),
            "current_meal": macrosToDict(currentMeal),
            "meal_index": mealIndex,
            "meals_per_day": mealsPerDay,
            "meal_name": mealName as Any,
            "diabetes_type": diabetesType as Any
        ]
        
        request.httpBody = try JSONSerialization.data(withJSONObject: body)
        
        let (data, _) = try await URLSession.shared.data(for: request)
        return try JSONDecoder().decode(MealComparison.self, from: data)
    }
    
    func getSuggestions(
        estimate: FoodEstimate,
        perMealTargets: Macros,
        dailyRemaining: Macros,
        mealName: String?,
        diabetesType: String?
    ) async throws -> MealSuggestions {
        let url = URL(string: "\(baseURL)/llm/suggestions")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let estimateData = try JSONEncoder().encode(estimate)
        let estimateDict = try JSONSerialization.jsonObject(with: estimateData) as! [String: Any]
        
        let body: [String: Any] = [
            "estimate": estimateDict,
            "per_meal_targets": macrosToDict(perMealTargets),
            "daily_remaining": macrosToDict(dailyRemaining),
            "meal_name": mealName as Any,
            "diabetes_type": diabetesType as Any
        ]
        
        request.httpBody = try JSONSerialization.data(withJSONObject: body)
        
        let (data, _) = try await URLSession.shared.data(for: request)
        return try JSONDecoder().decode(MealSuggestions.self, from: data)
    }
    
    func getDailySummary(
        date: String?,
        diabetesType: String?,
        meals: [MealRecord],
        dailyTargets: Macros,
        totalConsumed: Macros
    ) async throws -> DailySummary {
        let url = URL(string: "\(baseURL)/llm/daily_summary")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let mealsData: [[String: Any]] = meals.map { meal in
            let estimateData = try? JSONEncoder().encode(meal.estimate)
            let estimateDict = estimateData.flatMap { try? JSONSerialization.jsonObject(with: $0) as? [String: Any] }
            
            return [
                "timestamp": ISO8601DateFormatter().string(from: meal.timestamp),
                "meal_name": meal.mealName,
                "macros": macrosToDict(meal.macros),
                "estimate": estimateDict as Any
            ]
        }
        
        let body: [String: Any] = [
            "date": date as Any,
            "diabetes_type": diabetesType as Any,
            "meals": mealsData,
            "daily_targets": macrosToDict(dailyTargets),
            "total_consumed": macrosToDict(totalConsumed)
        ]
        
        request.httpBody = try JSONSerialization.data(withJSONObject: body)
        
        let (data, _) = try await URLSession.shared.data(for: request)
        return try JSONDecoder().decode(DailySummary.self, from: data)
    }
    
    private func macrosToDict(_ macros: Macros) -> [String: Double] {
        return [
            "protein_g": macros.proteinG,
            "fat_g": macros.fatG,
            "carb_g": macros.carbG,
            "kcal": macros.kcal
        ]
    }
}

enum APIError: Error {
    case invalidImage
    case networkError(String)
}

