# EO-SPECIFIC-LAYER.md — files scaffolded on top when the mode includes a backend

**Status:** living doc.
**Read by:** `handover-bridge` (Step 4b — after the mode subset lands, install the EO-specific layer on top).
**Applies to:** M1, M2, M3. Skipped for M0.

---

## Why this layer exists

Every EO project, regardless of mode, needs the same handful of founder-specific files that don't come from SaaSfast:

- The 5 founder profile fields (name, country code, company, industry, founder-since year)
- MENA-aware defaults (Cairo / Tajawal fonts, `dir="rtl"` wiring, Gulf phone prefixes)
- Distribution hooks (WhatsApp, GHL, Unifonic SMS fallback)
- Supabase RLS policy templates tuned for multi-tenant MENA data

Without this layer, every student repeats the same boilerplate. With it, `/1-eo-dev-start` hands off a repo where the **EO-specific decisions are already made** and the student focuses on their product, not plumbing.

---

## The 5 files (scaffolded on top of the mode subset)

### 1. `src/lib/founder-profile/schema.ts`

Extends Supabase's `auth.users` with 5 founder fields the EO ICP always needs:

```ts
export const founderProfileFields = [
  'full_name_ar',    // Arabic display name (required)
  'full_name_en',    // Latin display name (optional)
  'country',         // ISO code: AE, SA, EG, JO, KW, QA, BH, OM
  'company_name',    // legal entity (optional)
  'founder_since',   // year (integer, e.g. 2023)
];
```

Includes a matching Supabase migration at `supabase/migrations/0001_founder_profile.sql`.

### 2. `src/lib/mena-defaults/fonts.ts`

Sets Cairo + Tajawal as default fonts when `lang=ar`. Loads IBM Plex Sans when `lang=en`. Swap-safe — BRD can override per-project.

### 3. `src/lib/mena-defaults/phone.ts`

Country-code dropdown pre-sorted: UAE (+971), KSA (+966), KWT (+965), QAT (+974), BHR (+973), OMN (+968), EGY (+20), JOR (+962). Rest of world follows. Validation per E.164.

### 4. `src/lib/distribution/` (skeleton, wired lazy)

Three no-op clients the founder activates later:
- `whatsapp.ts` — Meta Business API wrapper. Env: `WHATSAPP_TOKEN`, `WHATSAPP_PHONE_ID`.
- `ghl.ts` — GoHighLevel webhook wrapper. Env: `GHL_WEBHOOK_URL`.
- `sms.ts` — Unifonic primary, Twilio fallback. Env: `UNIFONIC_APP_SID`, `UNIFONIC_SENDER_ID`, `TWILIO_*`.

Skeletons are `.ts` files with TODO markers + typed signatures. No network calls at scaffold time.

### 5. `supabase/policies/multi-tenant.sql`

Four RLS policies ready to copy-edit:
- `select_own_rows` — user can only read rows where `user_id = auth.uid()`
- `insert_own_rows` — user can only insert rows they own
- `update_own_rows` — same
- `admin_override` — service role bypass, scoped to admin operations

Each policy has a commented line explaining the MENA-specific reasoning (e.g. PDPL / SAMA data-residency rules).

---

## What `handover-bridge` does with this layer

After installing the mode subset (M1/M2/M3 per `SAASFAST-MODES.md`), copy the 5 files from this plugin's `skills/eo-dev-start/eo-layer/` directory into the project:

```
skills/eo-dev-start/eo-layer/founder-profile/        → $ROOT/src/lib/founder-profile/
skills/eo-dev-start/eo-layer/mena-defaults/          → $ROOT/src/lib/mena-defaults/
skills/eo-dev-start/eo-layer/distribution/           → $ROOT/src/lib/distribution/
skills/eo-dev-start/eo-layer/supabase-policies/      → $ROOT/supabase/policies/
skills/eo-dev-start/eo-layer/supabase-migrations/    → $ROOT/supabase/migrations/
```

If a file already exists at the destination → refuse; route to `/8-eo-dev-repair`. Never overwrite silently.

**Template files ship with this plugin** so the scaffold is reproducible and reviewable in PRs. When the layer evolves (e.g. a 6th founder field, a new distribution channel), the PR updates this doc + the template files in one change.

---

## What the layer is NOT

- **Not a product.** It's plumbing. The founder still builds every page and screen.
- **Not opinionated UI.** No components, no design tokens beyond fonts — those come from `brandvoice.md`.
- **Not authentication.** Auth is Supabase (via SaaSfast mode M1+). This layer just extends the user schema.
- **Not a lock-in.** Every file is plain TS/SQL. Delete what doesn't fit.

---

## Anti-patterns

- **Shipping the layer to M0 projects** — M0 is "not a web app." None of this applies. Skip.
- **Wiring distribution clients at scaffold time** — they're skeletons. Real tokens land when the founder opens an activation story.
- **Hard-coding country list in UI** — always import from `mena-defaults/phone.ts`. New country = one file change.
- **Skipping RLS policies** — even for a directory product, row-level security is non-negotiable. Every table gets one policy at minimum.

---

## Retro hook

If a student's project needs a 6th file on top of this layer (e.g. a Ramadan calendar helper, a Hijri-date formatter), capture via `/10-eo-retro`. When 2+ students hit the same gap → promote into this layer via PR.
