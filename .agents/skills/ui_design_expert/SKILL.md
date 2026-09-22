---
name: ui_design_expert
description: Advanced UI/UX design skill for modern web applications, covering visual hierarchy, design tokens, HSL color systems, dark mode elevation, fluid typography, 4px/8px layout grids, glassmorphism, micro-interactions, and WCAG accessibility standards.
---

# UI Design Expert Skill

When building or styling user interfaces, apply these principles and design patterns to create visually captivating, accessible, and high-performance applications.

---

## 1. Visual Hierarchy & Aesthetic Standards

* **First Impression Impact**: Deliver interfaces with curated color palettes, atmospheric dark modes, fluid typography, and subtle glassmorphism overlay effects.
* **Avoid Generic Defaults**:
  * Never use default browser fonts or basic raw red/blue/green colors.
  * Use custom HSL color palettes, tailored CSS variables, and modern web typography (e.g., *Inter*, *Outfit*, *Plus Jakarta Sans*, *Fira Code*).
* **Surface Elevation & Layering**:
  * In dark mode, build depth using stepped surface lightness (e.g., `#121212` base background -> `#1e1e24` card surface -> `#2a2a32` modal surface) rather than heavy drop shadows.
  * In light mode, combine soft ambient shadows (`0 8px 30px rgba(0,0,0,0.06)`) with subtle borders (`1px solid rgba(0,0,0,0.08)`).

---

## 2. Color System & Design Tokens

* **Semantic Token Architecture**:
  * Decouple color definitions from specific hex codes. Use semantic token names:
    * `--bg-primary`, `--bg-surface`, `--bg-elevated`
    * `--text-primary`, `--text-secondary`, `--text-muted`
    * `--accent-primary`, `--accent-hover`, `--accent-glow`
    * `--border-subtle`, `--border-active`
* **Accessibility & Contrast**:
  * Maintain WCAG 2.2 AA contrast ratio (minimum 4.5:1 for body text, 3:1 for large headers and UI controls).
  * Desaturate vibrant brand accent colors slightly in dark mode to prevent visual vibration on dark surfaces.

Detailed guidelines: [design_tokens_and_color_systems.md](file:///home/suresh/Desktop/trash/AI-LLM-security/.agents/skills/ui_design_expert/references/design_tokens_and_color_systems.md)

---

## 3. Typography & Spatial Layout Grids

* **Typography Scale**:
  * Implement a modular font scale (e.g., 1.25x major third or 1.333x perfect fourth).
  * Set optimal line height: `1.2` for display headers, `1.5` for body copy. Limit paragraph width to `65ch` to `75ch` for comfortable reading.
* **Strict Spacing Scale**:
  * Base layout grids on an **8px grid system** (or 4px micro-grid): `4px, 8px, 12px, 16px, 24px, 32px, 48px, 64px, 96px`.
  * Maintain consistent padding and margins using CSS utility variables or standardized spatial tokens.

Detailed guidelines: [typography_and_layout_grids.md](file:///home/suresh/Desktop/trash/AI-LLM-security/.agents/skills/ui_design_expert/references/typography_and_layout_grids.md)

---

## 4. Glassmorphism & Atmospheric Depth

* **Glassmorphism 2.0 Recipe**:
  * Combine `backdrop-filter: blur(12px) saturate(180%)`, semi-transparent backgrounds (`rgba(255, 255, 255, 0.08)` or `rgba(18, 18, 24, 0.65)`), and catch-light borders (`1px solid rgba(255, 255, 255, 0.12)`).
  * Use glassmorphism selectively for floating elements (navbars, modals, floating action bars, preview cards). Avoid applying heavy backdrop blurs to long-form text containers or dense data tables.

Detailed guidelines: [microinteractions_and_glassmorphism.md](file:///home/suresh/Desktop/trash/AI-LLM-security/.agents/skills/ui_design_expert/references/microinteractions_and_glassmorphism.md)

---

## 5. Micro-Interactions & Motion Design

* **Purposeful Micro-Animations**:
  * Keep interaction durations brief: `150ms` to `300ms`.
  * Use natural timing functions: `cubic-bezier(0.16, 1, 0.3, 1)` (ease-out-expo) for fast entry feedback.
  * Provide active feedback on button clicks (`transform: scale(0.98)`), card hovers (`transform: translateY(-2px)`), and focus states.
* **Performance**:
  * Only animate GPU-accelerated properties: `transform`, `opacity`, and `filter`. Avoid animating layout properties like `height`, `width`, `margin`, or `padding`.

---

## 6. Accessibility & Keyboard Navigation

* Always include explicit, high-contrast `:focus-visible` outline rings (`outline: 2px solid var(--accent-primary)` with `outline-offset: 2px`).
* Ensure all interactive elements have semantic tags (`<button>`, `<a>`, `<input>`) or explicit `role` and `aria-*` attributes.
