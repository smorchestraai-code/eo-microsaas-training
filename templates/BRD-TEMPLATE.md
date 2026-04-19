# BRD: [Feature Name]

**Created:** YYYY-MM-DD
**Status:** Draft / In Progress / Done
**Owner:** [you]

---

## Problem

*What user pain does this solve? One paragraph. Be specific.*

Example:
> Arabic-speaking SaaS founders in MENA can't easily test their pricing pages against Arabic-RTL edge cases. Free tools are English-only. Paid tools ($99/mo+) don't support Arabic. Founders end up shipping broken RTL pages and losing conversions.

## User (ICP)

*Who is this for? Concrete, not "everyone". Include role, context, constraint.*

Example:
> Bootstrap SaaS founder in Dubai/Riyadh/Amman, revenue $0-$50K/mo, shipping MENA-market product. Technical enough to run Vercel but doesn't have budget for a QA tester.

## What you'll build

*Bullet list. 5-10 items max.*

- [ ] Route `/pricing` that supports RTL mode
- [ ] 3 pricing tier cards with Arabic headers (Cairo font)
- [ ] Number display switches between English/Arabic numerals
- [ ] Mobile viewport tested at 375px, 390px, 414px
- [ ] CTA button follows cultural expectations (right-aligned for Arabic)

## Acceptance Criteria

*Numbered. Each one is testable. Tag your tests with `@AC-N.N` to match.*

- **AC-1.1** Landing page at `/pricing` returns HTTP 200
- **AC-1.2** When language is Arabic, all text is right-aligned (`dir="rtl"` on body)
- **AC-2.1** Primary CTA button is visible above the fold on 375px width
- **AC-2.2** Currency shows "ر.س" (Saudi Riyal) not "SAR" for Arabic users from Saudi
- **AC-3.1** Zero JavaScript console errors on landing
- **AC-4.1** Mobile (375px width) does not scroll horizontally

## Out of scope

*What are you explicitly NOT building in this cycle?*

- Checkout flow (next PR)
- Analytics integration
- Multiple Arabic dialects (Saudi only for v1)

## Dependencies

*What needs to exist before this can ship?*

- Supabase project provisioned (done)
- Cairo + Tajawal fonts in `public/fonts/` (need to add)
- Logo asset in RTL-friendly variant (need from designer)

## Done when

*What proves this is shipped?*

- [ ] All acceptance criteria pass
- [ ] Scorecard composite ≥ 90
- [ ] Lighthouse ≥ 90 on Performance + Accessibility
- [ ] Manually tested on real iPhone and Android
- [ ] Arabic native speaker reviewed for cultural correctness
- [ ] Deployed to production URL
- [ ] Link shared in community with one test user feedback

---

## Notes / Links

*Design files, research links, related BRDs.*

- Figma: [link]
- Competitor analysis: [doc]
- Related BRD: [BRD-checkout-flow.md]
