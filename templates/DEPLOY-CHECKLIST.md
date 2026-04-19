# Deploy Checklist (Student Edition)

**For:** Every deploy to Vercel / Netlify production.

---

## Before deploy (pre-flight)

- [ ] All acceptance criteria from BRD pass
- [ ] Scorecard composite ≥ 90
- [ ] `npm run build` succeeds locally
- [ ] `npm run start` serves built app correctly
- [ ] `.env.local` exists with real values (not committed)
- [ ] `.env.example` committed with placeholder values
- [ ] `NEXT_PUBLIC_*` vars configured in Vercel/Netlify dashboard
- [ ] Non-public env vars (secrets) set in dashboard WITHOUT `NEXT_PUBLIC_` prefix
- [ ] No `console.log` debug spam left in code
- [ ] No hardcoded URLs (use env vars for API endpoints)

## During deploy

- [ ] Deploy triggered (git push to main OR `vercel --prod`)
- [ ] Build succeeded in Vercel/Netlify dashboard (check logs)
- [ ] Deploy URL shown and accessible

## After deploy (smoke test)

- [ ] Open production URL — page loads
- [ ] Homepage renders (no 500)
- [ ] Main user flow works end-to-end
- [ ] Forms submit successfully (at least one)
- [ ] External API calls work (Supabase connects, Stripe responds, etc.)
- [ ] Mobile viewport (open on phone or DevTools)
- [ ] Arabic RTL (if applicable)
- [ ] Console has zero errors in production
- [ ] Lighthouse run: Performance ≥ 90, Accessibility ≥ 90

## Monitoring active?

- [ ] UptimeRobot (or similar) pings your URL every 5 min
- [ ] Sentry (or similar) catches client/server errors
- [ ] PostHog / Plausible / analytics wired

## Rollback plan

- [ ] Know how to rollback (Vercel dashboard → Deployments → Promote previous)
- [ ] Git SHA of last known-good version noted somewhere

## Record the deploy

Save to `docs/deployments/YYYY-MM-DD-v<version>.md`:

```markdown
# Deploy: v0.4.2 · 2026-04-19

**URL:** https://your-app.vercel.app
**Commit:** a7c3f89
**Branch:** main

## What changed
- Added password reset flow
- Fixed mobile layout on /pricing
- Upgraded Next.js 14.2.30 → 14.2.35

## Verification
- [x] smoke test passed
- [x] lighthouse 91 / 98 / 92 / 95
- [x] mobile Safari verified
- [x] Arabic RTL verified

## Known issues
- Stripe test mode — need to switch to live keys before launch
```

Tracking your deploys weekly is how you build operational muscle.
