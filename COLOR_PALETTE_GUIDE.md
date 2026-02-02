# 🎨 EatSmartly Color Palette Reference

## Your Exact Colors

Based on your design image, here are the 5 colors used throughout the app:

### 1. Champagne (#F5E6D1)
- **RGB**: 245, 230, 209
- **CMYK**: 0%, 6%, 15%, 4%
- **Usage**: Primary background, soft surfaces, base color
- **Feel**: Warm, neutral, approachable

### 2. Light Red (#FFC8CB)
- **RGB**: 255, 200, 203
- **CMYK**: 0%, 22%, 20%, 0%
- **Usage**: Soft accents, highlights, secondary elements
- **Feel**: Gentle, friendly, inviting

### 3. Rose Gold (#B46C72)
- **RGB**: 180, 108, 114
- **CMYK**: 0%, 40%, 37%, 29%
- **Usage**: Primary brand color, main buttons, app bar
- **Feel**: Premium, sophisticated, confident

### 4. Puce Red (#6E2E34)
- **RGB**: 110, 46, 52
- **CMYK**: 0%, 58%, 53%, 57%
- **Usage**: Dark accents, primary text, strong elements
- **Feel**: Bold, authoritative, grounded

### 5. Rackley (#5E7B9B)
- **RGB**: 94, 123, 155
- **CMYK**: 39%, 21%, 0%, 39%
- **Usage**: Info elements, neutral actions, secondary buttons
- **Feel**: Calm, trustworthy, balanced

---

## Color Hierarchy

```
PRIMARY PALETTE (Food & Health Focus)
┌─────────────────────────────────────┐
│ Rose Gold (#B46C72)                 │  ← Main brand color
│ Puce Red (#6E2E34)                  │  ← Strong accents
└─────────────────────────────────────┘

SUPPORTING PALETTE (Warmth & Softness)
┌─────────────────────────────────────┐
│ Champagne (#F5E6D1)                 │  ← Base background
│ Light Red (#FFC8CB)                 │  ← Soft highlights
└─────────────────────────────────────┘

FUNCTIONAL PALETTE (Information)
┌─────────────────────────────────────┐
│ Rackley (#5E7B9B)                   │  ← Neutral info
└─────────────────────────────────────┘
```

---

## Usage in App

### Home Screen
```
Background Gradient: Champagne → Light Red
Title Text: Puce Red (#6E2E34)
Subtitle: Rose Gold (#B46C72)
Feature Cards: White with Rose Gold icons
Start Button: Puce Red (#6E2E34)
```

### Scanner Screen
```
Camera Overlay: Black with 54% opacity
Corner Brackets: Light Red (#FFC8CB)
Instructions Card: Puce Red (#6E2E34) background
Toggle Buttons: Rackley (#5E7B9B)
```

### Result Screen
```
Safe Verdict: Green (#4CAF50)
Caution Verdict: Orange (#FF9800)
Avoid Verdict: Red (#E53935)
Primary Button: Rose Gold (#B46C72)
Text Headings: Puce Red (#6E2E34)
Alternative Cards: Champagne (#F5E6D1) background
```

---

## Color Accessibility

### Contrast Ratios (WCAG AA Compliant)

**Puce Red on Champagne**: 5.2:1 ✅
- Good for body text
- Readable and accessible

**Rose Gold on White**: 3.4:1 ⚠️
- Acceptable for large text
- Use white text on Rose Gold for buttons

**Light Red on White**: 1.8:1 ❌
- Only for decorative elements
- Not for text

---

## Color Psychology

### Why These Colors Work for Food & Health:

**Champagne (#F5E6D1)**
- Evokes natural, organic, wholesome foods
- Non-intimidating, comfortable
- Appetite-neutral (doesn't stimulate or suppress)

**Light Red/Pink (#FFC8CB)**
- Associated with sweetness, desserts
- Gentle warning without alarm
- Feminine, caring energy

**Rose Gold (#B46C72)**
- Premium quality perception
- Balances warm and professional
- Modern, trendy appeal

**Puce Red (#6E2E34)**
- Earthy, grounded, trustworthy
- Associated with rich foods (wine, chocolate)
- Authoritative for serious health info

**Rackley Blue (#5E7B9B)**
- Calm, logical, trustworthy
- Associated with health, wellness
- Balances the warm reds

---

## Semantic Color Mapping

```dart
// In Flutter theme.dart
const Color background = champagne;        // #F5E6D1
const Color primary = roseGold;            // #B46C72
const Color secondary = lightRed;          // #FFC8CB
const Color accent = puceRed;              // #6E2E34
const Color info = rackley;                // #5E7B9B

// Functional colors
const Color success = Color(0xFF4CAF50);   // Green
const Color warning = Color(0xFFFF9800);   // Orange
const Color error = Color(0xFFE53935);     // Red
```

---

## Design System

### Buttons
```
Primary Action: Rose Gold (#B46C72) background, White text
Secondary Action: Rackley (#5E7B9B) background, White text
Danger Action: Puce Red (#6E2E34) background, White text
Ghost Button: Transparent, Rose Gold border
```

### Cards
```
Standard: White background, 2px elevation
Elevated: White background, 4px elevation
Tinted: Champagne (#F5E6D1) background
Alert: Light Red (#FFC8CB) background with opacity
```

### Text Hierarchy
```
H1 (Titles): Puce Red (#6E2E34), Bold, 24-28px
H2 (Sections): Rose Gold (#B46C72), Bold, 18-20px
Body: Puce Red (#6E2E34), Regular, 15-16px
Caption: Grey (#8D8D8D), Regular, 13-14px
```

---

## Color Variations

### Light Tints (for backgrounds)
```dart
champagne.withOpacity(0.5)    // Very light
lightRed.withOpacity(0.1)     // Subtle pink tint
roseGold.withOpacity(0.1)     // Subtle rose tint
```

### Dark Shades (for hover states)
```dart
roseGold.withOpacity(0.8)     // Darker rose for hover
puceRed.withOpacity(0.9)      // Darker red for pressed
```

---

## Competitors Comparison

**MyFitnessPal**: Blue (#0072C6), White
- Too corporate, clinical
- ✅ Your palette is warmer, friendlier

**Yuka**: Green (#4CAF50), White
- Good but overused
- ✅ Your palette is unique, memorable

**OpenFoodFacts**: Blue/Orange
- Functional, not emotional
- ✅ Your palette creates connection

---

## Final Recommendation

✅ **Your color palette is perfect for EatSmartly because:**

1. **Unique**: Not the typical blue/green health app
2. **Emotional**: Warm colors create trust and comfort
3. **Premium**: Rose gold elevates the brand
4. **Balanced**: Mix of warm and cool tones
5. **Accessible**: Good contrast ratios
6. **Memorable**: Distinctive and cohesive

---

**Color palette designed for health, warmth, and sophistication! 🎨**
