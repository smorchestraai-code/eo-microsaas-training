# SAASFAST-MODES.md — the four modes, one picked per project

**Status:** living doc. Update via `/10-eo-retro` when a product doesn't fit any row.
**Read by:** `eo-dev-start` (Step 8b), `handover-bridge` (Step 4), `eo-dev-plan` (top of every plan), `eo-dev-repair` (mode-consistency check).
**Written to:** `$ROOT/architecture/tech-stack-decision.md` as a single `SaaSfast mode:` line + rationale. Every downstream command reads that line.

---

## The core idea

SaaSfast is a **toolkit**, not a stack. "Use SaaSfast" as a default boxes the UX — directory products don't want SaaSfast's dashboard; content sites don't want its auth-first landing. Architect-level there are four modes. Claude picks one based on the BRD + ICP, writes the choice, and every downstream command respects it.

Never edit SaaSfast-ar in place. Clone-to-new-folder only. Scaffold output goes into the BRD project slug folder.

---

## The four modes

| Mode | When it fits | What you pull from SaaSfast | What you build yourself | Typical product |
|------|--------------|-----------------------------|-------------------------|-----------------|
| **M0 — None** | Product is not a MicroSaaS web app (internal tool, CLI, API-only, mobile-first native). | Nothing. | Everything. Pick stack per BRD. | EO-internal admin CLI, Lana QA worker |
| **M1 — Backend-only** | Product has a custom frontend (directory, marketplace, content site, AppSumo-style browse+filter) but needs standard SaaS back-office. | `src/lib/supabase/`, `src/lib/payment/`, `src/lib/email/`, i18n/RTL wiring, `.env` contract. | All pages, all components, design system, routing. Hook into SaaSfast backend libs. | **EO Oasis MENA** (directory of MicroSaaS products) |
| **M2 — Gate-only** | Product is mostly its own app, but SaaSfast's landing + auth act as the marketing + entry point. Visitors land on SaaSfast pages, cross a gate into the custom app. | Landing page, auth flow, pricing page. Maybe payment. | Everything behind the gate — app UI, dashboards, domain logic. | Vertical SaaS with marketing site + app behind login |
| **M3 — Core stack** | Traditional SaaS (CRM, PM tool, admin-heavy). Dashboard + tables + admin are already close to what SaaSfast ships. | Everything. Extend in place. | Only domain-specific features + branding. | SalesMfast SME, internal admin consoles |

---

## How Claude picks (inside `eo-dev-start` Step 8b)

1. Read `$EO_BRAIN/4-Architecture/brd.md` — product description, target users, primary screens.
2. Read `$EO_BRAIN/4-Architecture/tech-stack-decision.md` if present.
3. Match first row whose signal appears:
   - BRD says "directory / marketplace / content site / catalog / browse + filter" → **M1**
   - BRD lists distinct marketing pages + product behind auth → **M2**
   - BRD describes login → dashboard → tables → features → **M3**
   - BRD is not a web app → **M0**
4. Ambiguous → **M1** (safe default — boring stuff for free, UX not boxed).
5. Print the decision + one-line rationale in the plan-mode preview. One approval. Move on.

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

A project's mode is picked once at `/1-eo-dev-start`. If the BRD evolves (e.g. a directory product adds a dashboard behind a paywall → mode should shift M1 → M2), the switch is made explicitly:

1. Update `architecture/tech-stack-decision.md` `SaaSfast mode:` line.
2. Run `/8-eo-dev-repair` — it reads the new mode, scaffolds the delta, and rescores.
3. Never silently upgrade the mode inside a story. Plan mode first, approval, then repair.

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

- **"Always use SaaSfast"** — boxes the UX for directory/content products. Always pick the mode, don't default to M3.
- **Editing SaaSfast-ar source** — never. Clone into the project slug folder, edit there.
- **Cross-mode scaffolding** — e.g. scaffolding dashboard shells in an M1 project "just in case." The mode is the contract. Break it only via explicit repair.
- **Asking the founder which mode to pick** — the BRD already answered. Claude reads, picks, prints rationale, asks approval once. No 5-question mode interview.
