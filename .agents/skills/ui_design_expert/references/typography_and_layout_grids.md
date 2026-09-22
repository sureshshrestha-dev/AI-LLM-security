# Typography & Layout Grids Reference

Guidelines for fluid typography scaling, vertical rhythm, and 8px/4px spatial grid systems.

---

## 1. Modular Typography Scale

Use CSS clamp or a proportional modular scale (1.25x Major Third ratio) for screen hierarchy.

```css
:root {
  --font-sans: 'Inter', 'Outfit', system-ui, -apple-system, sans-serif;
  --font-mono: 'Fira Code', 'JetBrains Mono', monospace;

  /* Font Sizes */
  --text-xs: clamp(0.75rem, 0.7rem + 0.25vw, 0.8125rem);   /* 12px - 13px */
  --text-sm: clamp(0.875rem, 0.83rem + 0.25vw, 0.9375rem);  /* 14px - 15px */
  --text-base: clamp(1rem, 0.95rem + 0.25vw, 1.0625rem);    /* 16px - 17px */
  --text-lg: clamp(1.125rem, 1.05rem + 0.35vw, 1.25rem);   /* 18px - 20px */
  --text-xl: clamp(1.35rem, 1.2rem + 0.75vw, 1.6rem);      /* 21.6px - 25.6px */
  --text-2xl: clamp(1.7rem, 1.45rem + 1.25vw, 2.15rem);   /* 27px - 34.4px */
  --text-3xl: clamp(2.15rem, 1.8rem + 1.75vw, 2.8rem);    /* 34px - 44.8px */

  /* Line Heights */
  --leading-tight: 1.2;
  --leading-snug: 1.35;
  --leading-normal: 1.5;
  --leading-relaxed: 1.625;
}
```

---

## 2. Spatial Grid System (8px Baseline)

All layout dimensions, margins, paddings, and gap tokens MUST adhere to an 8px grid (with a 4px micro-increment for compact components like badges or tags).

```css
:root {
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-6: 24px;
  --space-8: 32px;
  --space-12: 48px;
  --space-16: 64px;
  --space-24: 96px;

  --radius-sm: 6px;
  --radius-md: 10px;
  --radius-lg: 16px;
  --radius-full: 9999px;
}
```

---

## 3. Responsive Container Widths & Layout Patterns

* **Max Content Width**: `1280px` for main dashboards, `768px` for article reading views.
* **Gutters & Padding**: Minimum `16px` on mobile (`<640px`), `24px` on tablet, `32px` on desktop (`>1024px`).
* **Flexbox & Grid Alignment**:
  * Use `gap: var(--space-4)` instead of manual margins on child elements.
  * Use `grid-template-columns: repeat(auto-fit, minmax(280px, 1fr))` for responsive component grids without media queries.
