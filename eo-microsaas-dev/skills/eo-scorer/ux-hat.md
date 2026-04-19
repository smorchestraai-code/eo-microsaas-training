# UX Hat — Scoring Rubric

**Dimension:** Does it look and feel right? Mobile? Arabic RTL? Accessible?

**Time to score:** 2-3 minutes per PR (needs browser interaction)

---

## 8 Questions (each 1-10)

> **Before scoring:** open `docs/ux-reference/*.html` in a browser side-by-side
> with the rendered component. The artifacts are the UX ground truth from
> EO-Brain Phase 5. If the component doesn't match the artifact's layout,
> CTAs, or states → Q1 drops to 6 before any other question is asked.
> If no artifacts exist in `docs/ux-reference/` → UX hat caps at 8.


### 1. Mobile viewport 375px works
- ✅ 10: Tested on iPhone SE viewport (375x667). No horizontal scroll. All elements reachable by thumb.
- ⚠️ 7: Most elements work, 1 overlap at 375px
- ❌ 4: Designed for desktop, breaks below 768px
- 💀 1: Horizontal scrollbar on mobile

### 2. Arabic RTL (if MENA ICP)
- ✅ 10: `dir="rtl"` on body. Text right-aligned. Icons mirrored. Number format correct.
- ⚠️ 7: Basic RTL works but some icons/layouts wrong
- ❌ 4: RTL was considered but half-broken
- 💀 1: No RTL support; Arabic ICP is stated in BRD
- ⏭️ N/A: English-only ICP explicitly — skip this question

### 3. Fonts render correctly (MENA)
- ✅ 10: Cairo for headers, Tajawal for body, next/font optimization used
- ⚠️ 7: Right fonts but loading flash visible
- ❌ 4: Generic system fonts, not Arabic-optimized
- 💀 1: Tofu boxes where Arabic should render
- ⏭️ N/A: English-only

### 4. Zero JavaScript console errors
- ✅ 10: Devtools console clean on landing and during flow
- ⚠️ 7: 1-2 warnings (hydration or deprecation)
- ❌ 4: Several warnings including React warnings
- 💀 1: Uncaught errors, red text in console

### 5. Loading states present
- ✅ 10: Every async action shows a skeleton / spinner / disabled button
- ⚠️ 7: Most loading states present, 1-2 missing
- ❌ 4: UI blocks without feedback during loads
- 💀 1: User sees frozen UI, doesn't know if it's working

### 6. Accessibility basics (axe-core clean)
- ✅ 10: `npx @axe-core/playwright` scan returns 0 violations
- ⚠️ 7: 1-2 low-severity violations (contrast, redundant role)
- ❌ 4: Several moderate violations (missing alt, no labels)
- 💀 1: High-severity violations (keyboard trap, no skip-nav)

### 7. Responsive breakpoints tested
- ✅ 10: Works at 375px, 768px, 1024px, 1440px without visual regression
- ⚠️ 7: Works at mobile + desktop but awkward at tablet
- ❌ 4: Only desktop tested
- 💀 1: Breaks at common breakpoints

### 8. Cultural correctness (MENA if applicable)
- ✅ 10: Dates DD/MM/YYYY. Currency AED/SAR/QAR/KWD with proper symbol. Weekend = Fri/Sat. No Christmas imagery.
- ⚠️ 7: Most conventions correct, 1 off
- ❌ 4: US defaults assumed
- 💀 1: Hardcoded US locale (MM/DD/YYYY, $, Sun/Sat weekend)
- ⏭️ N/A: Not MENA ICP

---

## Mobile + Arabic test protocol (for the hat score)

Run BEFORE scoring:

1. Open Chrome DevTools → device toolbar → iPhone SE (375x667)
2. Walk through main user flow
3. Toggle language to Arabic if app has it
4. Walk through again in RTL
5. Open axe DevTools → run scan
6. Screenshot anything wrong

If you don't do these: cap UX hat at 6.

---

## Scoring

- Count ONLY non-N/A questions
- Sum answers, divide by count, × 1.25 = UX hat (capped at 10)

## Red flags that force UX ≤ 6

- Mobile not tested at 375px
- Known Arabic ICP but no RTL support
- Console has uncaught errors

## Red flags that force UX ≤ 3

- Keyboard navigation broken (critical a11y fail)
- Arabic text unreadable (Tofu / wrong direction)
- Mobile completely unusable (horizontal scroll + tiny touch targets)

## Calibration examples

See `calibration-examples.md`.
