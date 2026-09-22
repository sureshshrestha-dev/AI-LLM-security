# Design Tokens & Color Systems Reference

This guide details HSL color architecture, dark mode elevation surfaces, and semantic CSS variable naming conventions.

---

## 1. HSL Color Token Architecture

Using HSL (Hue, Saturation, Lightness) or OKLCH enables seamless opacity variations and dark mode adjustments using single variables.

```css
:root {
  /* Brand Hue Base */
  --brand-hue: 245;
  --brand-sat: 85%;

  /* Light Theme Colors */
  --bg-primary: hsl(var(--brand-hue), 20%, 98%);
  --bg-surface: hsl(var(--brand-hue), 15%, 100%);
  --bg-elevated: hsl(var(--brand-hue), 15%, 95%);

  --text-primary: hsl(var(--brand-hue), 40%, 10%);
  --text-secondary: hsl(var(--brand-hue), 15%, 40%);
  --text-muted: hsl(var(--brand-hue), 10%, 60%);

  --accent-primary: hsl(var(--brand-hue), var(--brand-sat), 55%);
  --accent-hover: hsl(var(--brand-hue), var(--brand-sat), 45%);
  --accent-glow: hsla(var(--brand-hue), var(--brand-sat), 55%, 0.25);

  --border-subtle: hsl(var(--brand-hue), 15%, 90%);
  --border-active: hsl(var(--brand-hue), 40%, 75%);
}

[data-theme="dark"],
.dark {
  /* Dark Theme Colors */
  --bg-primary: hsl(var(--brand-hue), 15%, 7%);
  --bg-surface: hsl(var(--brand-hue), 12%, 11%);
  --bg-elevated: hsl(var(--brand-hue), 10%, 16%);

  --text-primary: hsl(var(--brand-hue), 15%, 95%);
  --text-secondary: hsl(var(--brand-hue), 10%, 70%);
  --text-muted: hsl(var(--brand-hue), 8%, 50%);

  --accent-primary: hsl(var(--brand-hue), var(--brand-sat), 65%);
  --accent-hover: hsl(var(--brand-hue), var(--brand-sat), 75%);
  --accent-glow: hsla(var(--brand-hue), var(--brand-sat), 65%, 0.3);

  --border-subtle: hsl(var(--brand-hue), 10%, 18%);
  --border-active: hsl(var(--brand-hue), 25%, 35%);
}
```

---

## 2. Surface Elevation Layers in Dark Mode

In dark theme UIs, avoid using drop shadows to indicate elevation because light sources are not ambient. Instead, increase surface lightness (L in HSL):

1. **Base Canvas (`--bg-primary`)**: 7% - 9% lightness (e.g., `#121212` or `hsl(240, 15%, 8%)`).
2. **Card Surface (`--bg-surface`)**: 11% - 13% lightness.
3. **Elevated Elements / Dropdowns (`--bg-elevated`)**: 15% - 18% lightness.
4. **Modals & Dialogs**: 20% - 24% lightness with a subtle catch-light top border (`1px solid hsla(0, 0%, 100%, 0.1)`).

---

## 3. WCAG Contrast Compliance Rules

* Body copy MUST achieve minimum 4.5:1 contrast against its immediate background.
* Secondary/muted text MUST achieve minimum 3:1 contrast against its immediate background.
* Never use raw bright colors like `#FF0000` or `#00FF00` for alerts. Use desaturated, accessible hues:
  * **Success**: `hsl(150, 60%, 40%)` (light) / `hsl(150, 60%, 55%)` (dark)
  * **Warning**: `hsl(38, 92%, 48%)` (light) / `hsl(38, 92%, 60%)` (dark)
  * **Error**: `hsl(354, 70%, 54%)` (light) / `hsl(354, 70%, 65%)` (dark)
