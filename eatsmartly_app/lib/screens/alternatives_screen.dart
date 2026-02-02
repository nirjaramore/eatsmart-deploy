import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../theme.dart';
import 'result_screen.dart';

class AlternativesScreen extends StatefulWidget {
  final String barcode;
  final String productName;
  final String userId;

  const AlternativesScreen({
    Key? key,
    required this.barcode,
    required this.productName,
    required this.userId,
  }) : super(key: key);

  @override
  State<AlternativesScreen> createState() => _AlternativesScreenState();
}

class _AlternativesScreenState extends State<AlternativesScreen> {
  final EatSmartlyAPI api = EatSmartlyAPI();

  String selectedCriteria = 'all';
  bool isLoading = true;
  Map<String, dynamic>? alternativesData;
  String? error;

  final Map<String, String> criteriaLabels = {
    'all': 'Overall Healthier',
    'protein': 'Higher Protein',
    'sugar': 'Lower Sugar',
    'fat': 'Lower Fat',
    'fiber': 'Higher Fiber',
  };

  @override
  void initState() {
    super.initState();
    _loadAlternatives();
  }

  Future<void> _loadAlternatives() async {
    if (!mounted) return;
    setState(() {
      isLoading = true;
      error = null;
    });

    try {
      final data = await api.getAlternatives(
        widget.productName,
        widget.userId,
        criteria: selectedCriteria,
      );

      if (!mounted) return;
      setState(() {
        alternativesData = data;
        isLoading = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        error = e.toString().replaceAll('Exception: ', '');
        isLoading = false;
      });
    }
  }

  void _onCriteriaChanged(String? newCriteria) {
    if (newCriteria != null && newCriteria != selectedCriteria) {
      setState(() {
        selectedCriteria = newCriteria;
      });
      _loadAlternatives();
    }
  }

  Future<void> _viewAlternative(String barcode, String name) async {
    try {
      final analysis = await api.analyzeBarcode(
          barcode: barcode, userId: widget.userId, detailed: true);

      if (!mounted) return;
      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (context) => ResultScreen(analysis: analysis),
        ),
      );
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Error analyzing $name: ${e.toString()}'),
          backgroundColor: AppColors.error,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Better Alternatives'),
        elevation: 0,
      ),
      body: Column(
        children: [
          // Original product header
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: AppColors.primary,
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.1),
                  blurRadius: 4,
                  offset: const Offset(0, 2),
                ),
              ],
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Current Product:',
                  style: TextStyle(
                    color: Colors.white.withOpacity(0.9),
                    fontSize: 14,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  widget.productName,
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
          ),

          // Criteria selector
          Container(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Find alternatives with:',
                  style: TextStyle(
                    color: AppColors.textSecondary,
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 12),
                DropdownButtonFormField<String>(
                  value: selectedCriteria,
                  decoration: InputDecoration(
                    filled: true,
                    fillColor: Colors.white,
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                      borderSide: BorderSide(color: AppColors.primary),
                    ),
                    prefixIcon:
                        Icon(Icons.filter_list, color: AppColors.primary),
                  ),
                  items: criteriaLabels.entries.map((entry) {
                    return DropdownMenuItem(
                      value: entry.key,
                      child: Text(entry.value),
                    );
                  }).toList(),
                  onChanged: _onCriteriaChanged,
                ),
              ],
            ),
          ),

          // Alternatives list
          Expanded(
            child: _buildAlternativesList(),
          ),
        ],
      ),
    );
  }

  Widget _buildAlternativesList() {
    if (isLoading) {
      return Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            CircularProgressIndicator(color: AppColors.primary),
            const SizedBox(height: 16),
            Text(
              'Finding better options...',
              style: TextStyle(
                color: AppColors.textSecondary,
                fontSize: 16,
              ),
            ),
          ],
        ),
      );
    }

    if (error != null) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(Icons.error_outline, size: 64, color: AppColors.error),
              const SizedBox(height: 16),
              Text(
                error!,
                textAlign: TextAlign.center,
                style: TextStyle(color: AppColors.error, fontSize: 16),
              ),
              const SizedBox(height: 16),
              ElevatedButton(
                onPressed: _loadAlternatives,
                child: const Text('Retry'),
              ),
            ],
          ),
        ),
      );
    }

    final alternatives = alternativesData?['alternatives'] as List? ?? [];

    if (alternatives.isEmpty) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(Icons.search_off, size: 64, color: AppColors.textLight),
              const SizedBox(height: 16),
              Text(
                'No better alternatives found',
                style: TextStyle(
                  color: AppColors.textSecondary,
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                'This product is already a good choice!',
                textAlign: TextAlign.center,
                style: TextStyle(
                  color: AppColors.textLight,
                  fontSize: 14,
                ),
              ),
            ],
          ),
        ),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: alternatives.length,
      itemBuilder: (context, index) {
        final alternative = alternatives[index];
        return _buildAlternativeCard(alternative, index + 1);
      },
    );
  }

  Widget _buildAlternativeCard(Map<String, dynamic> alternative, int rank) {
    final String name = alternative['name'] ?? 'Unknown Product';
    final String? brand = alternative['brand'];
    final int score = alternative['score'] ?? 0;
    final List improvements = alternative['improvements'] ?? [];
    final Map nutrition = alternative['nutrition'] ?? {};
    final String? barcode = alternative['barcode'];

    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      elevation: 3,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: InkWell(
        onTap: barcode != null ? () => _viewAlternative(barcode, name) : null,
        borderRadius: BorderRadius.circular(16),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Rank badge and name
              Row(
                children: [
                  Container(
                    width: 36,
                    height: 36,
                    decoration: BoxDecoration(
                      color: rank <= 3 ? AppColors.success : AppColors.primary,
                      shape: BoxShape.circle,
                    ),
                    child: Center(
                      child: Text(
                        '#$rank',
                        style: const TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                          fontSize: 16,
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          name,
                          style: const TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                            color: AppColors.textPrimary,
                          ),
                        ),
                        if (brand != null)
                          Text(
                            brand,
                            style: TextStyle(
                              fontSize: 14,
                              color: AppColors.textSecondary,
                            ),
                          ),
                      ],
                    ),
                  ),
                  // Score badge
                  Container(
                    padding:
                        const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                    decoration: BoxDecoration(
                      color: AppColors.success.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(Icons.trending_up,
                            size: 16, color: AppColors.success),
                        const SizedBox(width: 4),
                        Text(
                          '+$score',
                          style: const TextStyle(
                            fontSize: 14,
                            fontWeight: FontWeight.bold,
                            color: AppColors.success,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),

              if (improvements.isNotEmpty) ...[
                const SizedBox(height: 12),
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: improvements.map<Widget>((improvement) {
                    return Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 10, vertical: 6),
                      decoration: BoxDecoration(
                        color: AppColors.success.withOpacity(0.15),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(Icons.check_circle,
                              size: 14, color: AppColors.success),
                          const SizedBox(width: 4),
                          Text(
                            improvement.toString(),
                            style: const TextStyle(
                              fontSize: 12,
                              fontWeight: FontWeight.w600,
                              color: AppColors.success,
                            ),
                          ),
                        ],
                      ),
                    );
                  }).toList(),
                ),
              ],

              // Nutrition summary
              const SizedBox(height: 12),
              const Divider(),
              const SizedBox(height: 8),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceAround,
                children: [
                  _buildNutrientInfo('Cal', nutrition['calories'], 'kcal'),
                  _buildNutrientInfo('Protein', nutrition['protein_g'], 'g'),
                  _buildNutrientInfo('Carbs', nutrition['carbs_g'], 'g'),
                  _buildNutrientInfo('Fat', nutrition['fat_g'], 'g'),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildNutrientInfo(String label, dynamic value, String unit) {
    final displayValue = value != null
        ? value is int
            ? value.toString()
            : (value as double).toStringAsFixed(1)
        : 'N/A';

    return Column(
      children: [
        Text(
          label,
          style: TextStyle(
            fontSize: 11,
            color: AppColors.textLight,
            fontWeight: FontWeight.w600,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          displayValue,
          style: const TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
            color: AppColors.textPrimary,
          ),
        ),
        Text(
          unit,
          style: TextStyle(
            fontSize: 10,
            color: AppColors.textLight,
          ),
        ),
      ],
    );
  }
}
