# EatSmart Website (Next.js + TypeScript)

This is a minimal Next.js + TypeScript scaffold with Tailwind CSS for the hero design you requested.

Setup

1. From the `eatsmartwebsite` folder install dependencies:

```bash
npm install
```

2. Copy your image to `public/asset/download (24).jpeg` (create the folders if needed). The project expects the image at that path.

3. Run the dev server:

```bash
npm run dev
```

Notes about the image and blue background removal

- I included a small SVG filter placeholder that attempts to de-emphasize blue backgrounds. Removing backgrounds perfectly may require editing the source image in an image editor or providing a transparent PNG / SVG. If you want, I can try to produce a stronger filter or guide a short image-edit workflow.

Files added

- `pages/` — Next.js pages (`index.tsx`, `_app.tsx`)
- `components/Hero.tsx` — hero section with heading and image
- `styles/globals.css` — Tailwind import + brand colors
- Tailwind/PostCSS config + `package.json` and `tsconfig.json`
