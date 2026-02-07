import easyocr
import sys

# Test OCR
reader = easyocr.Reader(['en'])
print("OCR reader initialized")

# Test with a simple image if provided
if len(sys.argv) > 1:
    image_path = sys.argv[1]
    results = reader.readtext(image_path)
    text = ' '.join([result[1] for result in results])
    print(f"Extracted text: {text}")
else:
    print("No image provided, OCR reader ready")