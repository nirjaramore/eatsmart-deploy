# EatSmartly Flutter App

Beautiful food analysis app with your custom color scheme.

## 🎨 Color Palette

- **Champagne** (#F5E6D1) - Light background
- **Light Red** (#FFC8CB) - Soft accent
- **Rose Gold** (#B46C72) - Primary brand color
- **Puce Red** (#6E2E34) - Dark accent
- **Rackley** (#5E7B9B) - Info/neutral

## 🚀 Quick Setup

### Prerequisites
- Flutter SDK installed (https://docs.flutter.dev/get-started/install)
- Android Studio or VS Code with Flutter extension
- Physical Android device or emulator

### Steps

1. **Navigate to app directory:**
```powershell
cd c:\Users\anany\projects\eatsmart\eatsmartly_app
```

2. **Get dependencies:**
```powershell
flutter pub get
```

3. **Configure backend URL:**

Open `lib/services/api_service.dart` and update the `baseUrl`:

For testing on **physical device**:
- Find your PC's IP address: `ipconfig` (look for IPv4)
- Use: `http://YOUR_PC_IP:8000`
- Example: `http://192.168.1.100:8000`

For testing on **Android emulator**:
- Use: `http://10.0.2.2:8000`

4. **Start the backend:**
```powershell
cd c:\Users\anany\projects\eatsmart\eatsmartly-backend
python main.py
```

5. **Run the app:**
```powershell
cd c:\Users\anany\projects\eatsmart\eatsmartly_app
flutter run
```

Or press **F5** in VS Code!

## 📱 App Features

### Home Screen
- Beautiful gradient background with your colors
- Feature cards explaining app capabilities
- "Start Scanning" button to begin

### Scanner Screen
- Live camera view with barcode scanning
- Custom overlay with corner brackets
- Flash and camera flip controls
- Real-time processing indicator

### Result Screen
- Food name and brand display
- Health score (0-100) with color coding
- Safety verdict (Safe/Caution/Avoid)
- Allergen alerts
- Personalized suggestions
- Healthier alternatives
- Detailed nutrition facts
- Scan another option

## 🔧 Configuration

### Update User ID

In `lib/screens/scanner_screen.dart`, change:
```dart
final String userId = 'test_user';
```

### Update API Endpoint

In `lib/services/api_service.dart`:
```dart
static const String baseUrl = 'http://YOUR_IP:8000';
```

## 🧪 Testing the Flow

1. **Start backend** (ensure it's running on port 8000)
2. **Run Flutter app**
3. **Tap "Start Scanning"**
4. **Point camera at a barcode**
5. **Wait for analysis** (loading indicator appears)
6. **View results** with health score and recommendations
7. **Tap "Scan Another"** to continue

## 📦 Test Barcodes

Common products to test:
- Coca-Cola: `012000814204`
- Snickers: `040000000891`
- Cheerios: `016000275287`
- Doritos: `028400056229`

You can manually enter these if needed (add search feature later).

## 🎯 Next Features to Add

- [ ] User authentication
- [ ] Profile management screen
- [ ] Search by food name
- [ ] Scan history
- [ ] Favorites
- [ ] Share results
- [ ] Dark mode
- [ ] Onboarding tutorial

## 🐛 Troubleshooting

### "Connection refused"
- Ensure backend is running
- Check your PC's firewall settings
- Verify IP address is correct
- For emulator, use `10.0.2.2:8000`

### "Camera permission denied"
- Go to app settings on your device
- Enable camera permission
- Restart the app

### "No barcode detected"
- Ensure good lighting
- Hold phone steady
- Try different angles
- Use a clear, printed barcode

### Build errors
```powershell
flutter clean
flutter pub get
flutter run
```

## 📸 Screenshots

(Add your app screenshots here after testing)

## 🔐 Security Notes

- Never commit API keys to git
- Use environment variables for production
- Implement proper authentication
- Use HTTPS in production

## 🚀 Building for Production

```powershell
# Build APK
flutter build apk --release

# Build App Bundle (for Play Store)
flutter build appbundle --release
```

---

**Enjoy your beautiful, color-coordinated food analyzer! 🎨🍎**
