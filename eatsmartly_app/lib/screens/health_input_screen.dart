import 'package:flutter/material.dart';
import '../theme.dart';
import 'main_screen.dart';

class HealthInputScreen extends StatefulWidget {
  const HealthInputScreen({Key? key}) : super(key: key);

  @override
  State<HealthInputScreen> createState() => _HealthInputScreenState();
}

class _HealthInputScreenState extends State<HealthInputScreen> {
  final _formKey = GlobalKey<FormState>();
  final TextEditingController _ageController = TextEditingController();
  final TextEditingController _weightController = TextEditingController();
  bool hasChronic = false;
  final Map<String, bool> vitamins = {
    'Vitamin A': false,
    'Vitamin B12': false,
    'Vitamin D': false,
    'Iron': false,
    'Vitamin C': false,
  };

  @override
  void dispose() {
    _ageController.dispose();
    _weightController.dispose();
    super.dispose();
  }

  void _submit() {
    if (!_formKey.currentState!.validate()) return;

    final age = int.tryParse(_ageController.text.trim()) ?? 0;
    final weight = double.tryParse(_weightController.text.trim()) ?? 0.0;
    final selectedVits =
        vitamins.entries.where((e) => e.value).map((e) => e.key).toList();

    // For now, we simply show a confirmation and move on to main app.
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
            'Saved — age: $age, weight: ${weight}kg, chronic: ${hasChronic ? 'yes' : 'no'}, vits: ${selectedVits.join(', ')}'),
        backgroundColor: AppColors.primary,
      ),
    );

    Navigator.pushReplacement(
      context,
      MaterialPageRoute(builder: (context) => const MainScreen()),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Your Health Profile'),
        elevation: 0,
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const SizedBox(height: 8),
                Text(
                  'Tell us a few things to personalize recommendations',
                  style: TextStyle(color: AppColors.textSecondary),
                ),
                const SizedBox(height: 16),
                TextFormField(
                  controller: _ageController,
                  keyboardType: TextInputType.number,
                  decoration: const InputDecoration(labelText: 'Age'),
                  validator: (v) {
                    final t = v?.trim();
                    if (t == null || t.isEmpty) return 'Please enter your age';
                    final n = int.tryParse(t);
                    if (n == null || n <= 0) return 'Enter a valid age';
                    return null;
                  },
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller: _weightController,
                  keyboardType: TextInputType.numberWithOptions(decimal: true),
                  decoration: const InputDecoration(labelText: 'Weight (kg)'),
                  validator: (v) {
                    final t = v?.trim();
                    if (t == null || t.isEmpty) return 'Enter your weight';
                    final n = double.tryParse(t);
                    if (n == null || n <= 0) return 'Enter a valid weight';
                    return null;
                  },
                ),
                const SizedBox(height: 12),
                CheckboxListTile(
                  value: hasChronic,
                  onChanged: (v) => setState(() => hasChronic = v ?? false),
                  title: const Text('Do you have any chronic disease?'),
                ),
                const SizedBox(height: 8),
                const Text('Are you deficient in any vitamins?'),
                ...vitamins.keys.map((k) {
                  return CheckboxListTile(
                    value: vitamins[k],
                    onChanged: (v) => setState(() => vitamins[k] = v ?? false),
                    title: Text(k),
                    controlAffinity: ListTileControlAffinity.leading,
                  );
                }).toList(),
                const Spacer(),
                ElevatedButton(
                  onPressed: _submit,
                  style: ElevatedButton.styleFrom(
                      minimumSize: const Size.fromHeight(56)),
                  child: const Text('Save and Continue'),
                ),
                const SizedBox(height: 12),
                TextButton(
                  onPressed: () {
                    Navigator.pushReplacement(
                      context,
                      MaterialPageRoute(
                          builder: (context) => const MainScreen()),
                    );
                  },
                  child: Text('Skip for now',
                      style: TextStyle(color: AppColors.textSecondary)),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
