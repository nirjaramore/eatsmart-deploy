import requests, json, sys
from main import ocr_space_extract

url = "https://via.placeholder.com/600x400.png?text=nutrition+label"
print("Downloading sample image...", file=sys.stderr)
try:
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    img = r.content
except Exception as e:
    print(f"Failed to download sample image: {e}", file=sys.stderr)
    raise

print("Calling ocr_space_extract...", file=sys.stderr)
try:
    res = ocr_space_extract(img)
    out = {
        "success": res.get("success"),
        "text_snippet": (res.get("text") or "")[:1000]
    }
    print(json.dumps(out, indent=2))
except Exception as e:
    print(f"OCR call failed: {e}", file=sys.stderr)
    raise
