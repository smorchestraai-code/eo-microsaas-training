# Business Requirements Document (BRD) — Canonical Fixture

**Product:** Test Product
**Version:** 1.0 (Weekend MVP + v2 roadmap)

> Cadence (Fri eve → Sun night) lives in `_dev-progress.md`. The BRD says **what**, not **when**.

---

## SCOPE

### Weekend MVP — what ships in 48 hrs (Stories 1-4)

| Loop | Story # | Story title |
|------|---------|-------------|
| auth | Story 1 | User Registration |
| domain | Story 2 | Core Action |
| money | Story 3 | Pricing + Checkout |
| notify | Story 2 | (welcome + receipt) |
| deploy | Story 4 | Production Deploy |
| observability | Story 4 | (Sentry + uptime) |
| compliance | Story 1 | (RLS policies) |

### v2 Roadmap — full product, post-weekend (Stories 5+, tagged `[@Phase2]`)

- Story 5: Advanced filtering
- Story 6: Admin moderation queue

### Explicitly Out of Scope — never building

- Native mobile app
- Marketplace API for third parties

---

## USER STORIES & ACCEPTANCE CRITERIA

### Story 1 [@WeekendMVP] [loop:auth] [loop:compliance]: User Registration

- **AC-1.1** Email registration form accepts RFC-5322-valid emails
- **AC-1.2** SMS 2FA sends a 6-digit OTP within 60 seconds
- **AC-1.3** Logout clears session + cookies
- **AC-1.4** Supabase RLS policy `select_own_rows` active on `users` table

### Story 2 [@WeekendMVP] [loop:domain] [loop:notify]: Core Action

- **AC-2.1** Primary action completes end-to-end with real DB write
- **AC-2.2** Welcome email fires on first action via Resend
- **AC-2.3** Error path returns useful message (not 500)

### Story 3 [@WeekendMVP] [loop:money]: Pricing + Checkout

- **AC-3.1** Pricing page renders 2-3 tiers
- **AC-3.2** Checkout redirect completes (sandbox)
- **AC-3.3** Webhook verifies signature; 401 on unsigned

### Story 4 [@WeekendMVP] [loop:deploy] [loop:observability]: Production Deploy

- **AC-4.1** Deployed on chosen lane; custom subdomain with SSL
- **AC-4.2** `/api/health` returns 200
- **AC-4.3** Sentry captures deliberate staging error within 30s

### Story 5 [@Phase2]: Advanced filtering

- **AC-5.1** Filter UI supports 5+ dimensions
- **AC-5.2** Server-side filter API with pagination
- **AC-5.3** Filter state persisted in URL

### Story 6 [@Phase2]: Admin moderation queue

- **AC-6.1** Admin dashboard lists pending submissions
- **AC-6.2** Per-submission scoring panel
- **AC-6.3** Audit log on every admin action
