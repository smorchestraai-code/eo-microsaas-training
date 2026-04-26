# SAASFAST-MODES.md — the four modes, one picked per project

**Status:** living doc. Update via `/10-eo-retro` when a product doesn't fit any row.
**Read by:** `eo-dev-start` (Step 8a + Step 8b), `handover-bridge` (Step 4), `eo-dev-plan` (top of every plan), `eo-dev-repair` (mode-consistency check).
**Written to:** `$ROOT/architecture/tech-stack-decision.md` as a single `SaaSfast mode:` line + rationale, prefixed by the founder's `SaaSfast: yes | no` answer from Step 8a. Every downstream command reads both lines.

---

## Founder agency comes first (Step 8a — always asked)

Before any heuristic runs, **`/1-eo-dev-start` always asks the founder** — in every bootstrap, no exceptions, no inference from the BRD: **"Will this project use SaaSfast — yes or no?"**

- `yes` → continue to Step 8b. The heuristic picks the right sub-mode (`M1` / `M2` / `M3`) from the BRD signal. The founder approves the recommended mode in the plan-mode preview before scaffolding starts.
- `no` → `saasfast_mode = M0` is locked. Step 8b is skipped entirely. Scaffold uses `tech-stack-decision.md` directly with **zero SaaSfast pieces** pulled in.

The BRD signal informs the recommendation; it never overrides the founder's first answer. This is the agency principle: the founder picks whether SaaSfast is in play; Claude picks how to leverage it once they've said yes.

---

## The core idea (when Step 8a returned `yes`)

SaaSfast is a **toolkit**, not a stack. "Use SaaSfast" as a default boxes the UX — directory products don't want SaaSfast's dashboard; content sites don't want its auth-first landing. Architect-level there are four modes. Once the founder says yes, Claude picks one mode based on the BRD + ICP, writes the choice, and every downstream command respects it.

Never edit SaaSfast-ar in place. Clone-to-new-folder only. Scaffold output goes into the BRD project slug folder.

---

## The four modes

| Mode | When it fits | What you pull from SaaSfast | What you build yourself | Typical product |
|------|--------------|-----------------------------|-------------------------|-----------------|
| **M0 — None** | Two paths: (a) Product is not a MicroSaaS web app (internal tool, CLI, API-only, mobile-first native). (b) Founder explicitly answered `no` in Step 8a. | Nothing. | Everything. Pick stack per BRD. | EO-internal admin CLI, Lana QA worker, or any project where the founder picked `no` at Step 8a |
| **M1 — Backend-only** | Product has a custom frontend (directory, marketplace, content site, AppSumo-style browse+filter) but needs standard SaaS back-office. | `src/lib/supabase/`, `src/lib/payment/`, `src/lib/email/`, i18n/RTL wiring, `.env` contract. | All pages, all components, design system, routing. Hook into SaaSfast backend libs. | **EO Oasis MENA** (directory of MicroSaaS products) |
| **M2 — Gate-only** | Product is mostly its own app, but SaaSfast's landing + auth act as the marketing + entry point. Visitors land on SaaSfast pages, cross a gate into the custom app. | Landing page, auth flow, pricing page. Maybe payment. | Everything behind the gate — app UI, dashboards, domain logic. | Vertical SaaS with marketing site + app behind login |
| **M3 — Core stack** | Traditional SaaS (CRM, PM tool, admin-heavy). Dashboard + tables + admin are already close to what SaaSfast ships. | Everything. Extend in place. | Only domain-specific features + branding. | SalesMfast SME, internal admin consoles |

---

## How Claude picks (inside `eo-dev-start` Step 8b — only when Step 8a returned `yes`)

If Step 8a returned `no`, Step 8b is skipped — `M0` is locked, this section does not run.

When Step 8a returned `yes`:

1. Read `$EO_BRAIN/4-Architecture/brd.md` — product description, target users, primary screens.
2. Read `$EO_BRAIN/4-Architecture/tech-stack-decision.md` if present.
3. Match first row whose signal appears:
   - BRD says "directory / marketplace / content site / catalog / browse + filter" → **M1**
   - BRD lists distinct marketing pages + product behind auth → **M2**
   - BRD describes login → dashboard → tables → features → **M3**
   - BRD is not a web app → **M0** (treat as auto-`no`; warn the founder their `yes` answer doesn't apply because the product isn't a web app)
4. Ambiguous → **M1** (safe default — boring stuff for free, UX not boxed).
5. Print the recommended mode + one-line rationale in the plan-mode preview, alongside the explicit `SaaSfast: yes` answer from Step 8a. The founder confirms both lines together. Move on.

---

## What each mode scaffolds (`handover-bridge` Step 4)

### M0 — None
- No SaaSfast libs. `src/` is created per BRD stack (Node CLI? static site? something else).
- Payment / email / auth only if BRD calls for them.

### M1 — Backend-only (default for directory products)
- `src/lib/supabase/` — auth + RLS helpers
- `src/lib/payment/<provider>/` — `stripe` by default, swap to `tap` / `hyperpay` / `moyasar` / `paytabs` per `payment_provider`
- `src/lib/email/` — Resend wrapper (SendGrid fallback)
- `src/lib/i18n/` + RTL wiring if `mena_flag=true`
- `.env.example` — Supabase URL/keys, payment keys, email keys
- **Not scaffolded:** SaaSfast's landing page, pricing page, auth UI pages, dashboard — the founder builds their own (or Claude does, to BRD spec).

### M2 — Gate-only
- Everything from M1 **plus**:
- `src/app/(marketing)/` — SaaSfast landing + pricing pages (edit in place)
- `src/app/(auth)/` — SaaSfast auth pages
- `src/app/(app)/` — empty shell for the custom app, gated by middleware

### M3 — Core stack
- Everything from M2 **plus**:
- `src/app/(app)/dashboard/` — SaaSfast dashboard shell
- `src/app/(app)/admin/` — SaaSfast admin shell
- `src/components/ui/` — full SaaSfast component library

---

## Mode-switching after the fact

A project's mode is picked once at `/1-eo-dev-start`. Three switch types are supported, all explicit:

**1. Mode shift within `yes` (e.g. M1 → M2 when a directory product adds a paywalled dashboard):**
1. Update `architecture/tech-stack-decision.md` `SaaSfast mode:` line.
2. Run `/8-eo-dev-repair` — it reads the new mode, scaffolds the delta, and rescores.

**2. Founder originally answered `no` and now wants to opt in:**
1. Update `architecture/tech-stack-decision.md`: change `SaaSfast: no` → `SaaSfast: yes`, add `SaaSfast mode: M1 (or whichever mode the BRD signals).`
2. Run `/8-eo-dev-repair` — it detects the `yes` flip, runs the Step 8b heuristic against the current BRD, prints the recommended mode for confirmation, then scaffolds the missing SaaSfast subset on top of the existing project.

**3. Founder originally answered `yes` and now wants to opt out:**
1. Update `architecture/tech-stack-decision.md`: change `SaaSfast: yes` → `SaaSfast: no`, change `SaaSfast mode:` to `M0`.
2. Run `/8-eo-dev-repair` — it does **not** auto-delete SaaSfast pieces (those are now founder-owned code). It records the opt-out and stops generating new SaaSfast scaffolds going forward. The founder can `git rm` what they don't want.

In all three cases: never silently change the mode inside a story. Plan mode first, approval, then repair.

---

## When none of the four fit

That's a lesson. Capture it via `/10-eo-retro`:
- What was the product's shape?
- Which mode came closest?
- What subset of SaaSfast was actually useful?
- Propose a new mode row (e.g. M4 — Hybrid content + app) with the same four columns above.

The retro writes a PR suggestion for this file. Next student benefits.

---

## Anti-patterns

- **Skipping Step 8a** — never. The founder is asked `yes/no` on every bootstrap, regardless of how clear the BRD signal is. Inferring `yes` from a SaaS-shaped BRD is a violation.
- **"Always use SaaSfast"** — boxes the UX for directory/content products. After Step 8a's `yes`, always pick the mode from the BRD signal — don't default to M3 just because SaaSfast ships a dashboard.
- **Editing SaaSfast-ar source** — never. Clone into the project slug folder, edit there.
- **Cross-mode scaffolding** — e.g. scaffolding dashboard shells in an M1 project "just in case." The mode is the contract. Break it only via explicit repair (one of the three switch types above).
- **Asking the founder a multi-choice mode interview** — Step 8a is one binary question (`yes/no`). Step 8b is a heuristic Claude runs and presents for one approval. There is no "pick M1 vs M2 vs M3" interview — the BRD signals which one fits.
