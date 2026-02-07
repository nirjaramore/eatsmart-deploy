import 'package:google_mlkit_text_recognition/google_mlkit_text_recognition.dart';
import '../models/food_analysis.dart';

class ParseResult {
  final DetailedNutrition nutrition;
  final int foundCount;
  final bool confident;

  ParseResult(
      {required this.nutrition,
      required this.foundCount,
      required this.confident});
}

double? _parseFirstNumber(String? s) {
  if (s == null) return null;
  final cleaned = s.replaceAll(',', '.');
  final reg = RegExp(r"([0-9]+(?:\.[0-9]+)?)");
  final m = reg.firstMatch(cleaned);
  if (m == null) return null;
  return double.tryParse(m.group(1)!);
}

// Attempt to parse nutrition from ML Kit RecognizedText using blocks/lines.
ParseResult parseNutritionFromRecognizedText(RecognizedText recognized) {
  final lines = <String>[];
  for (final block in recognized.blocks) {
    for (final line in block.lines) {
      final t = line.text.trim();
      if (t.isNotEmpty) lines.add(t);
    }
  }

  bool inNutritionTable = false;
  bool inIngredients = false;
  String? ingredients;

  double? calories;
  double? protein;
  double? carbs;
  double? sugar;
  double? addedSugar;
  double? fat;
  double? satFat;
  double? sodium;
  double? fiber;
  double? servingSize;

  for (var i = 0; i < lines.length; i++) {
    final raw = lines[i];
    final line = raw.toLowerCase();

    if (RegExp(r"nutrition|nutrition facts|amount per|per 100|per 100g|serving")
        .hasMatch(line)) {
      inNutritionTable = true;
    }

    if (RegExp(r"ingredient|ingredients|ingredientes").hasMatch(line)) {
      inIngredients = true;
      final idx = line.indexOf(RegExp(r"ingredient"));
      ingredients =
          raw.substring(idx + (line.contains('ingredients') ? 11 : 10)).trim();
      continue;
    }

    if (inIngredients) {
      // stop ingredients collection when another section likely starts
      if (RegExp(r"nutrition|fssai|batch|expiry|best before|manufactured")
          .hasMatch(line)) {
        inIngredients = false;
      } else {
        ingredients = (ingredients ?? '') + ' ' + raw.trim();
        continue;
      }
    }

    // Skip % Daily Value lines
    if (line.contains('%') && line.contains('daily')) continue;

    // If in nutrition table, look for nutrient names in the line and parse numbers
    if (inNutritionTable) {
      if (calories == null && RegExp(r"energy|calor|kcal|kj").hasMatch(line)) {
        calories = _parseFirstNumber(line);
      }
      if (protein == null && RegExp(r"\bprotein\b").hasMatch(line)) {
        protein = _parseFirstNumber(line) ?? _searchNearbyNumber(lines, i);
      }
      if (carbs == null &&
          RegExp(r"carbohydrat|\bcarb\b|total carbohydrate").hasMatch(line)) {
        carbs = _parseFirstNumber(line) ?? _searchNearbyNumber(lines, i);
      }
      if (addedSugar == null && RegExp(r"added sugar").hasMatch(line)) {
        addedSugar = _parseFirstNumber(line);
      }
      if (sugar == null && RegExp(r"\bsugar\b|total sugar").hasMatch(line)) {
        sugar = _parseFirstNumber(line) ?? _searchNearbyNumber(lines, i);
      }
      if (fat == null && RegExp(r"total fat|\bfat\b").hasMatch(line)) {
        fat = _parseFirstNumber(line) ?? _searchNearbyNumber(lines, i);
      }
      if (satFat == null &&
          RegExp(r"saturat|sat fat|saturated").hasMatch(line)) {
        satFat = _parseFirstNumber(line) ?? _searchNearbyNumber(lines, i);
      }
      if (sodium == null && RegExp(r"sodium|salt").hasMatch(line)) {
        sodium = _parseFirstNumber(line) ?? _searchNearbyNumber(lines, i);
        if (sodium != null && line.contains('g') && !line.contains('mg'))
          sodium = sodium * 1000;
      }
      if (fiber == null && RegExp(r"fiber|fibre").hasMatch(line)) {
        fiber = _parseFirstNumber(line) ?? _searchNearbyNumber(lines, i);
      }
      if (servingSize == null &&
          RegExp(r"serving size|serving|per 100").hasMatch(line)) {
        final m = RegExp(r"([0-9]+(?:\.[0-9]+)?)\s*(g|mg)").firstMatch(line);
        if (m != null) {
          servingSize = double.tryParse(m.group(1)!);
          if (m.group(2) == 'mg' && servingSize != null)
            servingSize = servingSize / 1000.0;
        }
      }
    } else {
      // Not in nutrition table: still try to catch single-line nutrients
      if (calories == null && RegExp(r"energy|calor|kcal|kj").hasMatch(line))
        calories = _parseFirstNumber(line);
    }
  }

  // If addedSugar present, prefer it for sugar if sugar is null
  if (sugar == null && addedSugar != null) sugar = addedSugar;

  // Count found nutrients
  final found = [calories, protein, carbs, fat, sugar, sodium]
      .where((e) => e != null)
      .length;
  final confident = found >= 4;

  return ParseResult(
    nutrition: DetailedNutrition(
      servingSize: servingSize,
      servingUnit: servingSize != null ? 'g' : null,
      calories: calories,
      proteinG: protein,
      carbsG: carbs,
      fatG: fat,
      saturatedFatG: satFat,
      sodiumMg: sodium,
      sugarG: sugar,
      fiberG: fiber,
      ingredients: ingredients?.trim(),
    ),
    foundCount: found,
    confident: confident,
  );
}

// Look for a number in nearby lines (previous or next) as a fallback for table parsing
double? _searchNearbyNumber(List<String> lines, int index) {
  for (var offset = 1; offset <= 2; offset++) {
    final prev = index - offset;
    if (prev >= 0) {
      final n = _parseFirstNumber(lines[prev]);
      if (n != null) return n;
    }
    final next = index + offset;
    if (next < lines.length) {
      final n = _parseFirstNumber(lines[next]);
      if (n != null) return n;
    }
  }
  return null;
}
