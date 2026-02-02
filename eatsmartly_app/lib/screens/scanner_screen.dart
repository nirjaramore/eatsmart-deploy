import 'package:flutter/material.dart';
import 'package:mobile_scanner/mobile_scanner.dart';
import '../services/api_service.dart';
import '../theme.dart';
import 'result_screen.dart';

class ScannerScreen extends StatefulWidget {
  const ScannerScreen({Key? key}) : super(key: key);

  @override
  State<ScannerScreen> createState() => _ScannerScreenState();
}

class _ScannerScreenState extends State<ScannerScreen> {
  final EatSmartlyAPI api = EatSmartlyAPI();
  final String userId = 'test_user'; // Replace with actual user ID from auth

  MobileScannerController cameraController = MobileScannerController();
  bool isProcessing = false;
  String? error;
  String statusMessage = 'Analyzing product...';
  int progressStep = 0;

  @override
  void dispose() {
    cameraController.dispose();
    super.dispose();
  }

  Future<void> _analyzeBarcode(String barcode) async {
    if (isProcessing) return;

    if (!mounted) return;
    setState(() {
      isProcessing = true;
      error = null;
      statusMessage = 'Scanning barcode: $barcode';
      progressStep = 1;
    });

    // Update progress messages
    _updateProgress(2, 'Searching Open Food Facts India...');
    await Future.delayed(const Duration(milliseconds: 500));

    _updateProgress(3, 'Checking global food databases...');
    await Future.delayed(const Duration(milliseconds: 500));

    _updateProgress(4, 'Cross-verifying nutrition data...');

    try {
      final result = await api.analyzeBarcode(
          barcode: barcode, userId: userId, detailed: true);

      _updateProgress(5, 'Analysis complete!');
      await Future.delayed(const Duration(milliseconds: 300));

      if (mounted) {
        // Navigate to results screen
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => ResultScreen(analysis: result),
          ),
        ).then((_) {
          // Reset state when coming back
          if (mounted) {
            setState(() {
              isProcessing = false;
              progressStep = 0;
              statusMessage = 'Analyzing product...';
            });
          }
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          error = e.toString().replaceAll('Exception: ', '');
          isProcessing = false;
          progressStep = 0;
        });
      }

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(error ?? 'Unknown error'),
            backgroundColor: AppColors.error,
            duration: const Duration(seconds: 5),
            action: SnackBarAction(
              label: 'Retry',
              textColor: Colors.white,
              onPressed: () => _analyzeBarcode(barcode),
            ),
          ),
        );
      }
    }
  }

  void _updateProgress(int step, String message) {
    if (!mounted) return;
    setState(() {
      progressStep = step;
      statusMessage = message;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Scan Barcode'),
      ),
      body: Stack(
        children: [
          // Camera view
          MobileScanner(
            controller: cameraController,
            onDetect: (capture) {
              final List<Barcode> barcodes = capture.barcodes;
              if (barcodes.isNotEmpty && !isProcessing) {
                final barcode = barcodes.first.rawValue;
                if (barcode != null && barcode.isNotEmpty) {
                  _analyzeBarcode(barcode);
                }
              }
            },
          ),

          // Scanning overlay
          CustomPaint(
            painter: ScannerOverlayPainter(),
            child: Container(),
          ),

          // Instructions
          Positioned(
            top: 40,
            left: 0,
            right: 0,
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
              child: Card(
                color: AppColors.primary.withOpacity(0.9),
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Text(
                    'Position the barcode within the frame',
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      color: AppColors.textOnDark,
                      fontSize: 16,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ),
              ),
            ),
          ),

          // Loading indicator
          if (isProcessing)
            Container(
              color: Colors.black54,
              child: Center(
                child: Card(
                  child: Padding(
                    padding: const EdgeInsets.all(24),
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        CircularProgressIndicator(
                          color: AppColors.primary,
                          value: progressStep / 5,
                        ),
                        const SizedBox(height: 16),
                        Text(
                          statusMessage,
                          textAlign: TextAlign.center,
                          style: TextStyle(
                            color: AppColors.textPrimary,
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          'Step $progressStep of 5',
                          style: TextStyle(
                            color: AppColors.textSecondary,
                            fontSize: 12,
                          ),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          'This may take up to 60 seconds',
                          style: TextStyle(
                            color: AppColors.textLight,
                            fontSize: 11,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),

          // Bottom controls
          Positioned(
            bottom: 40,
            left: 0,
            right: 0,
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                // Toggle flash
                FloatingActionButton(
                  heroTag: 'flash',
                  backgroundColor: AppColors.info,
                  onPressed: () => cameraController.toggleTorch(),
                  child: const Icon(Icons.flash_on),
                ),

                // Flip camera
                FloatingActionButton(
                  heroTag: 'flip',
                  backgroundColor: AppColors.info,
                  onPressed: () => cameraController.switchCamera(),
                  child: const Icon(Icons.flip_camera_ios),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

/// Custom painter for scanner overlay
class ScannerOverlayPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.black54
      ..style = PaintingStyle.fill;

    final scanArea = Rect.fromCenter(
      center: Offset(size.width / 2, size.height / 2),
      width: size.width * 0.7,
      height: size.height * 0.4,
    );

    // Draw dark overlay with transparent scan area
    final path = Path()
      ..addRect(Rect.fromLTWH(0, 0, size.width, size.height))
      ..addRRect(RRect.fromRectAndRadius(scanArea, const Radius.circular(16)))
      ..fillType = PathFillType.evenOdd;

    canvas.drawPath(path, paint);

    // Draw corner brackets
    final bracketPaint = Paint()
      ..color = AppColors.secondary
      ..style = PaintingStyle.stroke
      ..strokeWidth = 4;

    const bracketLength = 30.0;

    // Top-left
    canvas.drawLine(
      Offset(scanArea.left, scanArea.top + bracketLength),
      Offset(scanArea.left, scanArea.top),
      bracketPaint,
    );
    canvas.drawLine(
      Offset(scanArea.left, scanArea.top),
      Offset(scanArea.left + bracketLength, scanArea.top),
      bracketPaint,
    );

    // Top-right
    canvas.drawLine(
      Offset(scanArea.right - bracketLength, scanArea.top),
      Offset(scanArea.right, scanArea.top),
      bracketPaint,
    );
    canvas.drawLine(
      Offset(scanArea.right, scanArea.top),
      Offset(scanArea.right, scanArea.top + bracketLength),
      bracketPaint,
    );

    // Bottom-left
    canvas.drawLine(
      Offset(scanArea.left, scanArea.bottom - bracketLength),
      Offset(scanArea.left, scanArea.bottom),
      bracketPaint,
    );
    canvas.drawLine(
      Offset(scanArea.left, scanArea.bottom),
      Offset(scanArea.left + bracketLength, scanArea.bottom),
      bracketPaint,
    );

    // Bottom-right
    canvas.drawLine(
      Offset(scanArea.right - bracketLength, scanArea.bottom),
      Offset(scanArea.right, scanArea.bottom),
      bracketPaint,
    );
    canvas.drawLine(
      Offset(scanArea.right, scanArea.bottom - bracketLength),
      Offset(scanArea.right, scanArea.bottom),
      bracketPaint,
    );
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
