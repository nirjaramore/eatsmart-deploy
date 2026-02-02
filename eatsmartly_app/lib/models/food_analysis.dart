class FoodAnalysis {
  final String barcode;
  final String? foodName;
  final String? brand;
  final String verdict;
  final String riskLevel;
  final double healthScore;
  final List<String> alerts;
  final List<String> warnings;
  final List<String> suggestions;
  final List<Alternative> alternatives;
  final List<Recipe> recipes;
  final List<String> nutritionTips;
  final DetailedNutrition? detailedNutrition;
  final String timestamp;

  FoodAnalysis({
    required this.barcode,
    this.foodName,
    this.brand,
    required this.verdict,
    required this.riskLevel,
    required this.healthScore,
    required this.alerts,
    required this.warnings,
    required this.suggestions,
    required this.alternatives,
    required this.recipes,
    required this.nutritionTips,
    this.detailedNutrition,
    required this.timestamp,
  });

  factory FoodAnalysis.fromJson(Map<String, dynamic> json) {
    return FoodAnalysis(
      barcode: json['barcode'] ?? '',
      foodName: json['food_name'],
      brand: json['brand'],
      verdict: json['verdict'] ?? 'unknown',
      riskLevel: json['risk_level'] ?? 'low',
      healthScore: (json['health_score'] ?? 0).toDouble(),
      alerts: List<String>.from(json['alerts'] ?? []),
      warnings: List<String>.from(json['warnings'] ?? []),
      suggestions: List<String>.from(json['suggestions'] ?? []),
      alternatives:
          (json['alternatives'] as List? ?? [])
              .map((a) => Alternative.fromJson(a))
              .toList(),
      recipes:
          (json['recipes'] as List? ?? [])
              .map((r) => Recipe.fromJson(r))
              .toList(),
      nutritionTips: List<String>.from(json['nutrition_tips'] ?? []),
      detailedNutrition:
          json['detailed_nutrition'] != null
              ? DetailedNutrition.fromJson(json['detailed_nutrition'])
              : null,
      timestamp: json['timestamp'] ?? DateTime.now().toIso8601String(),
    );
  }
}

class Alternative {
  final String name;
  final String reason;

  Alternative({required this.name, required this.reason});

  factory Alternative.fromJson(Map<String, dynamic> json) {
    return Alternative(name: json['name'] ?? '', reason: json['reason'] ?? '');
  }
}

class Recipe {
  final String title;
  final String url;
  final String source;

  Recipe({required this.title, required this.url, required this.source});

  factory Recipe.fromJson(Map<String, dynamic> json) {
    return Recipe(
      title: json['title'] ?? '',
      url: json['url'] ?? '',
      source: json['source'] ?? '',
    );
  }
}

class DetailedNutrition {
  final double? servingSize;
  final String? servingUnit;
  final double? calories;
  final double? proteinG;
  final double? carbsG;
  final double? fatG;
  final double? saturatedFatG;
  final double? sodiumMg;
  final double? sugarG;
  final double? fiberG;
  final String? ingredients;
  final List<String>? allergens;

  DetailedNutrition({
    this.servingSize,
    this.servingUnit,
    this.calories,
    this.proteinG,
    this.carbsG,
    this.fatG,
    this.saturatedFatG,
    this.sodiumMg,
    this.sugarG,
    this.fiberG,
    this.ingredients,
    this.allergens,
  });

  factory DetailedNutrition.fromJson(Map<String, dynamic> json) {
    return DetailedNutrition(
      servingSize: json['serving_size']?.toDouble(),
      servingUnit: json['serving_unit'],
      calories: json['calories']?.toDouble(),
      proteinG: json['protein_g']?.toDouble(),
      carbsG: json['carbs_g']?.toDouble(),
      fatG: json['fat_g']?.toDouble(),
      saturatedFatG: json['saturated_fat_g']?.toDouble(),
      sodiumMg: json['sodium_mg']?.toDouble(),
      sugarG: json['sugar_g']?.toDouble(),
      fiberG: json['fiber_g']?.toDouble(),
      ingredients: json['ingredients'],
      allergens:
          json['allergens'] != null
              ? List<String>.from(json['allergens'])
              : null,
    );
  }
}

class UserProfile {
  final int? age;
  final String? gender;
  final double? heightCm;
  final double? weightKg;
  final String? activityLevel;
  final String? healthGoal;
  final List<String> allergies;
  final List<String> healthConditions;
  final List<String> dietaryRestrictions;

  UserProfile({
    this.age,
    this.gender,
    this.heightCm,
    this.weightKg,
    this.activityLevel,
    this.healthGoal,
    this.allergies = const [],
    this.healthConditions = const [],
    this.dietaryRestrictions = const [],
  });

  factory UserProfile.fromJson(Map<String, dynamic> json) {
    return UserProfile(
      age: json['age'],
      gender: json['gender'],
      heightCm: json['height_cm']?.toDouble(),
      weightKg: json['weight_kg']?.toDouble(),
      activityLevel: json['activity_level'],
      healthGoal: json['health_goal'],
      allergies: List<String>.from(json['allergies'] ?? []),
      healthConditions: List<String>.from(json['health_conditions'] ?? []),
      dietaryRestrictions: List<String>.from(
        json['dietary_restrictions'] ?? [],
      ),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'age': age,
      'gender': gender,
      'height_cm': heightCm,
      'weight_kg': weightKg,
      'activity_level': activityLevel,
      'health_goal': healthGoal,
      'allergies': allergies,
      'health_conditions': healthConditions,
      'dietary_restrictions': dietaryRestrictions,
    };
  }
}
