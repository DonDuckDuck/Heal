//
//  DataModels.swift
//  Heal
//

import Foundation

struct UserProfile: Codable {
    let heightCm: Double
    let weightKg: Double
    let age: Int
    let sex: String
    let exerciseLevel: String
    let diabetesType: String
    let mealsPerDay: Int
    let mealTimes: [String]
}

struct Macros: Codable, Equatable {
    let proteinG: Double
    let fatG: Double
    let carbG: Double
    let kcal: Double
    
    enum CodingKeys: String, CodingKey {
        case proteinG = "protein_g"
        case fatG = "fat_g"
        case carbG = "carb_g"
        case kcal
    }
}

struct DailyBudget: Codable {
    let dailyBudget: Macros
    let perMealTargets: Macros
    let macroSplit: MacroSplit
    let mealsPerDay: Int
    
    enum CodingKeys: String, CodingKey {
        case dailyBudget = "daily_budget"
        case perMealTargets = "per_meal_targets"
        case macroSplit = "macro_split"
        case mealsPerDay = "meals_per_day"
    }
}

struct MacroSplit: Codable {
    let protein: Double
    let carb: Double
    let fat: Double
}

struct FoodEstimate: Codable {
    let items: [FoodItem]
    let totals: Macros
    let caloriesRange: CalorieRange
    let assumptions: [String]
    let warnings: [String]
    let modelInfo: String
    
    enum CodingKeys: String, CodingKey {
        case items, totals, assumptions, warnings
        case caloriesRange = "calories_range"
        case modelInfo = "model_info"
    }
}

struct FoodItem: Codable, Identifiable {
    var id: UUID = UUID()
    let name: String
    let displayName: String
    let category: String
    let cookingMethod: String
    let grams: Double
    let kcal: Double
    let nutritionPer100g: Macros
    let confidence: Double
    let notes: [String]
    
    enum CodingKeys: String, CodingKey {
        case name, displayName = "display_name", category
        case cookingMethod = "cooking_method", grams, kcal
        case nutritionPer100g = "nutrition_per_100g"
        case confidence, notes
    }
    
    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        self.name = try container.decode(String.self, forKey: .name)
        self.displayName = try container.decode(String.self, forKey: .displayName)
        self.category = try container.decode(String.self, forKey: .category)
        self.cookingMethod = try container.decode(String.self, forKey: .cookingMethod)
        self.grams = try container.decode(Double.self, forKey: .grams)
        self.kcal = try container.decode(Double.self, forKey: .kcal)
        self.nutritionPer100g = try container.decode(Macros.self, forKey: .nutritionPer100g)
        self.confidence = try container.decode(Double.self, forKey: .confidence)
        self.notes = try container.decode([String].self, forKey: .notes)
        self.id = UUID()
    }
}

struct CalorieRange: Codable {
    let low: Double
    let high: Double
}

struct MealRecord: Identifiable {
    let id = UUID()
    let timestamp: Date
    let mealIndex: Int
    let mealName: String
    let estimate: FoodEstimate
    let macros: Macros
    let imageData: Data?
}

struct MealComparison: Codable {
    let perMealEvaluation: MacroEvaluation
    let dailyEvaluationPostMeal: DailyEvaluation
    let flags: ComparisonFlags
    let progressBars: ProgressBars
    let notes: [String]
    let modelInfo: String
    
    enum CodingKeys: String, CodingKey {
        case perMealEvaluation = "per_meal_evaluation"
        case dailyEvaluationPostMeal = "daily_evaluation_post_meal"
        case flags, progressBars = "progress_bars", notes, modelInfo = "model_info"
    }
}

struct MacroEvaluation: Codable {
    let proteinG: NutrientStatus
    let carbG: NutrientStatus
    let fatG: NutrientStatus
    
    enum CodingKeys: String, CodingKey {
        case proteinG = "protein_g"
        case carbG = "carb_g"
        case fatG = "fat_g"
    }
}

struct NutrientStatus: Codable {
    let target: Double
    let actual: Double
    let difference: Double
    let status: String
    let percentOfTarget: Double
    
    enum CodingKeys: String, CodingKey {
        case target, actual, difference, status
        case percentOfTarget = "percent_of_target"
    }
}

struct DailyEvaluation: Codable {
    let proteinG: DailyNutrientStatus
    let carbG: DailyNutrientStatus
    let fatG: DailyNutrientStatus
    
    enum CodingKeys: String, CodingKey {
        case proteinG = "protein_g"
        case carbG = "carb_g"
        case fatG = "fat_g"
    }
}

struct DailyNutrientStatus: Codable {
    let targetDaily: Double
    let consumedSoFar: Double
    let afterMeal: Double
    let remaining: Double
    let willExceedBy: Double
    let percentOfDailyTargetAfterMeal: Double
    
    enum CodingKeys: String, CodingKey {
        case targetDaily = "target_daily"
        case consumedSoFar = "consumed_so_far"
        case afterMeal = "after_meal"
        case remaining
        case willExceedBy = "will_exceed_by"
        case percentOfDailyTargetAfterMeal = "percent_of_daily_target_after_meal"
    }
}

struct ComparisonFlags: Codable {
    let perMealExceededAny: Bool
    let dailyExceededAny: Bool
    let overPerMeal: [String]
    let overDaily: [String]
    
    enum CodingKeys: String, CodingKey {
        case perMealExceededAny = "per_meal_exceeded_any"
        case dailyExceededAny = "daily_exceeded_any"
        case overPerMeal = "over_per_meal"
        case overDaily = "over_daily"
    }
}

struct ProgressBars: Codable {
    let perMealPercent: ProgressPercent
    let dailyPercentAfterMeal: ProgressPercent
    
    enum CodingKeys: String, CodingKey {
        case perMealPercent = "per_meal_percent"
        case dailyPercentAfterMeal = "daily_percent_after_meal"
    }
}

struct ProgressPercent: Codable {
    let proteinG: Double
    let carbG: Double
    let fatG: Double
    
    enum CodingKeys: String, CodingKey {
        case proteinG = "protein_g"
        case carbG = "carb_g"
        case fatG = "fat_g"
    }
}

struct MealSuggestions: Codable {
    let actions: [Action]
    let adjustedMacrosAfterActions: Macros
    let rationale: [String]
    let modelInfo: String
    
    enum CodingKeys: String, CodingKey {
        case actions
        case adjustedMacrosAfterActions = "adjusted_macros_after_actions"
        case rationale, modelInfo = "model_info"
    }
}

struct Action: Codable, Identifiable {
    var id: UUID = UUID()
    let kind: String
    let text: String
    let estimatedEffect: Macros?
    
    enum CodingKeys: String, CodingKey {
        case kind, text
        case estimatedEffect = "estimated_effect"
        // id is not from JSON, it's auto-generated locally
    }
    
    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        self.kind = try container.decode(String.self, forKey: .kind)
        self.text = try container.decode(String.self, forKey: .text)
        self.estimatedEffect = try container.decodeIfPresent(Macros.self, forKey: .estimatedEffect)
        self.id = UUID()  // Generate new ID for each decoded action
    }
}

struct DailySummary: Codable {
    let summaryPoints: [String]
    let nextDayFocus: [String]
    let macroOverview: MacroOverview
    let alerts: [String]
    let modelInfo: String
    
    enum CodingKeys: String, CodingKey {
        case summaryPoints = "summary_points"
        case nextDayFocus = "next_day_focus"
        case macroOverview = "macro_overview"
        case alerts, modelInfo = "model_info"
    }
}

struct MacroOverview: Codable {
    let proteinG: String
    let carbG: String
    let fatG: String
    
    enum CodingKeys: String, CodingKey {
        case proteinG = "protein_g"
        case carbG = "carb_g"
        case fatG = "fat_g"
    }
}

