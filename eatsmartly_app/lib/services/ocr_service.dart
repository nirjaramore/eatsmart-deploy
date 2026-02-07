import 'package:google_mlkit_text_recognition/google_mlkit_text_recognition.dart';

/// Recognize text from an image file path using ML Kit Text Recognition.
Future<RecognizedText> recognizeTextFromFile(String path) async {
  final inputImage = InputImage.fromFilePath(path);
  final textRecognizer = TextRecognizer(script: TextRecognitionScript.latin);
  final RecognizedText recognised =
      await textRecognizer.processImage(inputImage);
  await textRecognizer.close();
  return recognised;
}
