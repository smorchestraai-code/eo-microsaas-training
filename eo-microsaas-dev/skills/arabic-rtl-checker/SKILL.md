# arabic-rtl-checker — MENA UI Compliance

**Purpose:** Catch Arabic RTL failures before they ship. MENA ICP means Arabic is primary, not secondary.

**Pillar:** EO-specific — MENA quality gate
**Time cost:** 3-5 minutes per PR with UI changes.

---

## When to run

**Mandatory for any PR that:**
- Adds/modifies a React component with user-facing text
- Adds/modifies a form, modal, or navigation element
- Changes spacing, alignment, or icon positioning
- Adds new copy (English OR Arabic)

**Skip only if:**
- Pure backend change (no UI)
- Internal admin tool with English-only ICP explicitly stated in BRD

---

## The 8-point checklist

For every changed component, verify:

### 1. `dir="rtl"` respected
- [ ] Component renders correctly when parent has `dir="rtl"`
- [ ] No hard-coded `left/right` values; use `start/end` (Tailwind: `ms-*` / `me-*` not `ml-*` / `mr-*`)

### 2. Text alignment mirrors
- [ ] Headings right-align in Arabic, left-align in English
- [ ] Body copy flows from right in Arabic
- [ ] Lists bullet from the right in Arabic

### 3. Icons mirror (directional only)
- [ ] Back/forward arrows flip (use CSS `transform: scaleX(-1)` or RTL-aware icon set)
- [ ] Chevrons in dropdowns flip
- [ ] Progress bars fill right-to-left in Arabic
- [ ] NON-directional icons (home, user, settings) do NOT flip

### 4. Fonts correct
- [ ] Arabic text renders in Cairo (headers) or Tajawal (body)
- [ ] No tofu boxes (□□□) anywhere
- [ ] No mixed English/Arabic font sizing mismatch
- [ ] `next/font` optimization in use (no FOIT/FOUT flash)

### 5. Numbers render correctly
- [ ] Western Arabic numerals (0-9) by default for financial/data
- [ ] Eastern Arabic numerals (٠-٩) only if explicitly requested
- [ ] Currency symbol position: AED/SAR AFTER number in Arabic, BEFORE in English
- [ ] Thousands separator: comma for English, Arabic comma `،` or space for Arabic

### 6. Mixed content handled
- [ ] English brand names inside Arabic text render LTR within RTL paragraph
- [ ] URLs + email addresses render LTR
- [ ] Code snippets render LTR
- [ ] Use `<bdi>` or `unicode-bidi: isolate` for mixed direction

### 7. Forms work RTL
- [ ] Label position: right of input in RTL
- [ ] Input text cursor starts on right in Arabic
- [ ] Placeholder aligns right in Arabic
- [ ] Error messages align right in Arabic
- [ ] Checkbox/radio: box on right, label on left in RTL

### 8. Layout primitives mirror
- [ ] Flex `flex-row` becomes reverse in RTL (use `flex-row-reverse` or `dir`-aware CSS)
- [ ] Grid column order reverses in RTL
- [ ] Margin/padding directional: use logical properties (`padding-inline-start`)
- [ ] Floats: use `float: inline-start` / `inline-end`

---

## Test protocol (run before scoring)

```bash
# 1. Add dir="rtl" to <html> or <body> in your local env
# 2. Toggle language to Arabic in the app
# 3. Walk through:
#    - Home page
#    - Main form
#    - Modal / dialog
#    - Navigation
#    - Error state
# 4. Screenshot each view
# 5. Compare side-by-side with English version
```

If the screenshots aren't in the PR description: **UX hat caps at 6**.

---

## Common failures + fixes

| Failure | Root cause | Fix |
|---------|------------|-----|
| Text left-aligns in Arabic | Hardcoded `text-left` | Use `text-start` (Tailwind 3.3+) or conditional class |
| Margin is wrong side | `ml-4` / `mr-4` | Use `ms-4` / `me-4` |
| Chevron points wrong way | Static icon | Use `rtl:rotate-180` modifier |
| Tofu boxes | Font not loaded | Verify Cairo/Tajawal in `next/font` + preload |
| Arabic + English mixed oddly | No BiDi isolation | Wrap in `<bdi>` |
| Currency "100 AED" shows in Arabic as "AED 100" | No locale-aware formatter | Use `Intl.NumberFormat('ar-AE', {style:'currency', currency:'AED'})` |
| Form label below input in RTL | `flex-row` not mirrored | Add `rtl:flex-row-reverse` |

---

## Automated checks (add to CI)

```bash
# grep for hard-coded direction classes that break RTL
grep -rE "\b(ml|mr|pl|pr|left|right)-[0-9]+\b" src/components/ \
  --include="*.tsx" --include="*.jsx" \
  | grep -v "rtl:" \
  | grep -v "// rtl-ok"
```

If output is non-empty → fail the check. Either refactor to `ms-*`/`me-*` or tag with `// rtl-ok` comment explaining why it's directional.

---

## Integration

- **ux-hat Q2** uses this skill's checklist
- **/eo-review** runs this check on any PR touching `src/components/**/*.tsx`
- **lessons-manager** captures repeat RTL failures as lessons

---

## Reference tools

- Chrome DevTools → Rendering → "Emulate CSS media feature prefers-reduced-data" + manually set `dir="rtl"`
- `react-intl` or `next-intl` for locale-aware formatting
- [RTL Styling Guide](https://rtlstyling.com/) by Ahmad Shadeed
- Tailwind `rtl:` modifier (v3.3+)
