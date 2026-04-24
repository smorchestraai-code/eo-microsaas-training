# mena-mobile-check — 375px + MENA Context Verification

**Purpose:** MENA users are mobile-first. 70%+ of traffic is iPhone at 375x667. If it doesn't work there, it doesn't ship.

**Pillar:** EO-specific — MENA quality gate
**Time cost:** 2-3 minutes per PR with UI changes.

---

## The viewport matrix (test all 4 before UX hat ≥ 8)

| Device | Width | Why |
|--------|-------|-----|
| iPhone SE | 375x667 | Baseline — if it breaks here, it breaks for 30% of MENA |
| iPhone 14 Pro | 393x852 | Modern iPhone average |
| iPad Mini | 768x1024 | Tablet breakpoint check |
| Desktop | 1440x900 | Founder/office viewing |

---

## The 10-point mobile check

### 1. No horizontal scrollbar at 375px
- [ ] Body has no overflow-x
- [ ] All fixed widths removed; use `max-w-full`

### 2. Touch targets ≥ 44x44px
- [ ] Buttons, links, form controls all ≥ 44px tap area (Apple HIG)
- [ ] Icon-only buttons have padding to reach 44px

### 3. Font size ≥ 16px for body
- [ ] Body text ≥ 16px (prevents iOS zoom-on-focus)
- [ ] Form inputs ≥ 16px (same reason)
- [ ] Arabic body ≥ 17px (Tajawal x-height smaller than Latin)

### 4. Thumb-reachable CTAs
- [ ] Primary CTA in bottom 2/3 of screen (thumb zone)
- [ ] Destructive actions NOT in thumb zone (prevent mis-tap)
- [ ] Sticky bottom bar on long forms

### 5. Viewport meta tag
```html
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
```
- [ ] Present in `<head>`
- [ ] No `user-scalable=no` (accessibility fail)

### 6. Images responsive
- [ ] `next/image` with explicit `sizes`
- [ ] No fixed `width="800"` on `<img>`
- [ ] `object-fit: cover` on hero images

### 7. Forms usable
- [ ] Labels visible above inputs (not floating that hide value)
- [ ] Phone inputs use `type="tel"` + country code dropdown with UAE +971 / KSA +966 / QAT +974 / KWT +965 defaults
- [ ] Email inputs use `type="email"` + `autocomplete="email"`
- [ ] Date inputs use native mobile picker
- [ ] Error messages visible without scrolling

### 8. No hover-only affordances
- [ ] Tooltips accessible via tap, not hover
- [ ] Dropdowns open on tap, not hover
- [ ] No "hover to reveal" content

### 9. Modals fit 375px
- [ ] Modal width ≤ 100vw - 32px (16px margin each side)
- [ ] Modal height ≤ 100vh - 100px (space for keyboard)
- [ ] Close button in reachable position (top-right in LTR, top-left in RTL)
- [ ] Scrollable if content exceeds viewport

### 10. Loading states visible
- [ ] Skeleton / spinner on async actions
- [ ] Button disabled + spinner during submit (not frozen)
- [ ] Toast confirmations reachable (not hidden behind keyboard)

---

## MENA cultural correctness

### Dates
- Format: DD/MM/YYYY (not US MM/DD/YYYY)
- Month names in Arabic: use `Intl.DateTimeFormat('ar-AE')`

### Currency
| Country | Code | Symbol | Example |
|---------|------|--------|---------|
| UAE | AED | د.إ or AED | 250 AED |
| KSA | SAR | ر.س or SAR | 250 SAR |
| Qatar | QAR | ر.ق or QAR | 250 QAR |
| Kuwait | KWD | د.ك or KWD | 25.000 KWD (3 decimals!) |

- [ ] Currency symbol position correct per locale
- [ ] KWD uses 3 decimals, others use 2
- [ ] No `$` as default — auto-detect country from profile or IP

### Weekend
- [ ] Calendar treats Friday + Saturday as weekend (UAE, KSA, Qatar, Kuwait)
- [ ] "Next business day" logic skips Fri/Sat, not Sat/Sun

### Phone numbers
- [ ] Country dropdown defaults to UAE/KSA/QAT/KWT at top
- [ ] Validation accepts +971, +966, +974, +965 formats
- [ ] Display format: +971 50 123 4567 (space-separated)

### Imagery
- [ ] No alcohol, pork, revealing attire
- [ ] No Christmas/Easter/Halloween assumed
- [ ] Ramadan-aware: no food imagery in Ramadan marketing
- [ ] Prayer time awareness: no "24/7" promises that conflict with cultural norms

---

## Test protocol

```bash
# 1. Chrome DevTools → Device toolbar → iPhone SE (375x667)
# 2. Walk the main flow: land → signup → core action → success
# 3. Screenshot each screen
# 4. Switch language to Arabic → repeat
# 5. Check all touch targets with DevTools inspector (show hit areas)
# 6. Run `npx @axe-core/playwright` for a11y scan
# 7. Paste screenshots + axe output into PR description
```

If this protocol isn't evidenced in the PR: **UX hat caps at 6**.

---

## Integration

- **ux-hat Q1, Q7, Q8** use this checklist
- **/4-eo-review** runs visual check on any PR touching `src/**/*.tsx`
- **lessons-manager** captures mobile regressions
- **/eo-qa** runs Playwright tests at 375px viewport

---

## Quick-reference Tailwind breakpoints

```
Default (0-639px)   → Mobile (test at 375px)
sm:  (640px+)       → Large mobile / small tablet
md:  (768px+)       → Tablet
lg:  (1024px+)      → Desktop
xl:  (1280px+)      → Wide desktop
```

**Rule:** Design mobile-first. Every style without a breakpoint prefix must work at 375px.
