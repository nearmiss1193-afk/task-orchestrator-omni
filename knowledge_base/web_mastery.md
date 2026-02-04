# EMPIRE WEB MASTERY: The Sovereign Standard
>
> "Attention is the new oil. Beauty is the drill."

## 1. The Psychology of Capture (0-3 Seconds)

- **The Hook:** Above the fold MUST contain a "Visceral Promise". Not just text, but an emotion.
  - *Example:* Instead of "We fix ACs", use "Sleep Cool Tonight. Or It's Free."
- **Visual Hierarchy:** Eyes follow the F-pattern (Western). Key CTA must interrupt this flow at the "Terminal Point" (bottom right of the first scan).
- **Motion:** Subtle particle effects or "breathing" buttons trigger the reptilian brain's motion detector. (Use `framer-motion` or CSS keyframes).

## 2. Retention Engineering (Engagement)

- **Micro-Interactions:** Every click, hover, and scroll must have a reaction. The site must feel "alive".
- **Glassmorphism & Depth:** Use aggressive blurring (`backdrop-filter: blur(12px)`) and multi-layered shadows to create a 3D space on a 2D screen. Premium feels "heavy" and "deep".
- **Typography:** Mix a geometric sans-serif (Inter/Outfit) for headers with a highly readable serif or humanist sans for body. High contrast (OSE: #0f172a vs #e2e8f0).

## 3. Visual Compliance (The Shield)

- **ADA (Americans with Disabilities Act):**
  - All images MUST have descriptive `alt` tags.
  - Color contrast ratio > 4.5:1 for normal text.
  - Focus states (`ring-2`) visible for keyboard navigation.
- **GDPR / CCPA:**
  - "Cookie Consent" must be explicit but non-intrusive (Bottom-left floating pill, not a wall).
  - "Do Not Sell My Info" link in footer.
- **Trust Signals:** SSL Padlock, Physical Address, and Privacy Policy visible on every page.

## 4. The "Sovereign" Aesthetic (Tailwind Config)

- **Colors:**
  - Primary: `slate-950` (The Void)
  - Accent: `blue-500` to `purple-600` (The Energy)
  - Text: `slate-100` (The Signal)
- **Borders:** `border-white/10` (The Glass Edge)
- **Gradients:** `bg-gradient-to-br from-slate-900 via-slate-950 to-black`

## 5. Technical SEO

- **Core Web Vitals:** Must be optimized for maximum speed.
- **Semantic HTML:** `<main>`, `<article>`, `<nav>`, not just `<div>` soup.
- **Schema.org:** JSON-LD identifying the Organization, LocalBusiness, and Service.
