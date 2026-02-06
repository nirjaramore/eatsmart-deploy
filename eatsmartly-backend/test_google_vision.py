#!/usr/bin/env python3
"""
Test Google Cloud Vision OCR functionality
"""
import os
import io
from PIL import Image, ImageDraw, ImageFont
from google.cloud import vision
from google.oauth2 import service_account

def create_test_image():
    """Create a simple test image with nutrition text"""
    # Create a white image
    img = Image.new('RGB', (400, 200), color='white')
    draw = ImageDraw.Draw(img)

    # Try to use a default font, fallback to basic if not available
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()

    # Add nutrition text
    text = """Nutrition Facts
Serving Size: 28g
Calories: 150
Total Fat: 8g
Protein: 2g
Carbs: 18g"""

    # Draw text on image
    y_position = 20
    for line in text.split('\n'):
        draw.text((20, y_position), line, fill='black', font=font)
        y_position += 25

    return img

def test_google_vision():
    """Test Google Cloud Vision OCR"""
    try:
        # Path to service account key
        key_path = os.path.join(os.path.dirname(__file__), 'eatsmartly-vision-key.json')

        if not os.path.exists(key_path):
            print(f"❌ Service account key not found at: {key_path}")
            return False

        # Create credentials
        credentials = service_account.Credentials.from_service_account_file(key_path)

        # Initialize Vision client
        client = vision.ImageAnnotatorClient(credentials=credentials)
        print("✅ Google Cloud Vision client initialized")

        # Create test image
        test_image = create_test_image()

        # Convert to bytes
        img_byte_arr = io.BytesIO()
        test_image.save(img_byte_arr, format='PNG')
        img_bytes = img_byte_arr.getvalue()

        # Create Vision image object
        image = vision.Image(content=img_bytes)

        # Perform text detection
        print("🔍 Performing OCR...")
        response = client.document_text_detection(image=image)

        # Extract text
        if response.text_annotations:
            extracted_text = response.text_annotations[0].description
            print("✅ OCR successful!")
            print(f"📝 Extracted text:\n{extracted_text}")

            # Check if key nutrition terms are found
            text_lower = extracted_text.lower()
            found_terms = []
            for term in ['calories', 'fat', 'protein', 'carbs', 'serving']:
                if term in text_lower:
                    found_terms.append(term)

            print(f"🔍 Found nutrition terms: {found_terms}")
            return True
        else:
            print("❌ No text detected in image")
            return False

    except Exception as e:
        print(f"❌ Google Vision test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Google Cloud Vision OCR...")
    success = test_google_vision()
    if success:
        print("✅ Google Vision OCR test passed!")
    else:
        print("❌ Google Vision OCR test failed!")