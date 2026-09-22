# Micro-Interactions & Glassmorphism Reference

Recipes for modern glass visual effects, GPU-accelerated micro-animations, and interactive state feedback.

---

## 1. Glassmorphism CSS Snippets

### Standard Glass Panel
```css
.glass-panel {
  background: rgba(255, 255, 255, 0.07);
  backdrop-filter: blur(16px) saturate(180%);
  -webkit-backdrop-filter: blur(16px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.12);
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2);
}

.dark .glass-panel {
  background: rgba(18, 18, 24, 0.65);
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.45);
}
```

### Interactive Glass Card (Hover Effect)
```css
.glass-card {
  transition: transform 250ms cubic-bezier(0.16, 1, 0.3, 1),
              box-shadow 250ms cubic-bezier(0.16, 1, 0.3, 1),
              border-color 250ms ease;
  will-change: transform;
}

.glass-card:hover {
  transform: translateY(-4px);
  border-color: rgba(255, 255, 255, 0.25);
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.3);
}
```

---

## 2. Micro-Interactions & Motion Tokens

### Easing Functions
```css
:root {
  --ease-out-expo: cubic-bezier(0.16, 1, 0.3, 1);
  --ease-out-back: cubic-bezier(0.34, 1.56, 0.64, 1);
  --ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);

  --duration-fast: 150ms;
  --duration-normal: 250ms;
  --duration-slow: 400ms;
}
```

### Tactile Button Feedback
```css
.btn-tactile {
  transition: transform var(--duration-fast) var(--ease-out-expo),
              background-color var(--duration-fast) ease,
              box-shadow var(--duration-fast) ease;
}

.btn-tactile:hover {
  transform: translateY(-1px);
}

.btn-tactile:active {
  transform: translateY(1px) scale(0.98);
}
```

### Focus Ring Indicator (Accessibility)
```css
*:focus-visible {
  outline: 2px solid var(--accent-primary);
  outline-offset: 3px;
  border-radius: var(--radius-sm);
}
```

---

## 3. Motion Safety (`prefers-reduced-motion`)

Always respect user preferences for reduced motion:

```css
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```
