# Student SOP: Deployment (Vercel / Netlify)

**Version:** 1.0 (2026-04-19)
**When to use:** When you're ready to put your MicroSaaS on a real URL.

---

## Pick a platform

| If your project is... | Use | Free tier enough? |
|----------------------|-----|-------------------|
| Next.js app | **Vercel** | Yes, 100GB bandwidth/mo |
| Static HTML / React SPA | **Netlify** | Yes, 100GB bandwidth/mo |
| Node.js backend (not serverless) | **Render** or **Railway** | Render free tier is limited; Railway charges per-usage |
| Python / Ruby / other | **Render** or **Fly.io** | Render free tier works |

For MicroSaaS MVPs: **Vercel for Next.js, Netlify for static** are the standard.

---

## Vercel setup (Next.js)

```bash
# 1. Install Vercel CLI
npm i -g vercel

# 2. Login (opens browser)
vercel login

# 3. From your project folder, deploy (first time sets up the project)
cd your-project
vercel

# Answer prompts:
# - Setup and deploy? yes
# - Link to existing project? no
# - Project name: your-project
# - Directory: ./
# - Modify settings? no

# 4. To deploy to production:
vercel --prod
```

Every `git push` to `main` will auto-deploy after you connect the repo in Vercel dashboard.

### Vercel env vars

Add in Vercel dashboard: Your project → Settings → Environment Variables.

**Critical:**
- `NEXT_PUBLIC_*` vars are visible to the browser (not for secrets)
- Server-side secrets (Supabase service role key, Stripe secret) go without the `NEXT_PUBLIC_` prefix
- Never put secrets in code or in `.env.local` that's committed

---

## Netlify setup (static / React SPA)

```bash
# 1. Push your repo to GitHub first
# 2. Go to netlify.com → New site from Git
# 3. Select your GitHub repo
# 4. Build command: npm run build
# 5. Publish directory: dist (Vite) or build (CRA) or .next (Next.js)
```

Every `git push` to `main` auto-deploys.

### Netlify env vars

Site settings → Build & deploy → Environment → Environment variables.

---

## Before first deploy (checklist)

- [ ] `.env.example` committed with placeholder values (no real secrets)
- [ ] `.env.local` is in `.gitignore`
- [ ] `npm run build` succeeds locally
- [ ] Basic routes work locally (`npm run start` after `npm run build`)
- [ ] Database (if any) has tables + RLS policies set up in Supabase
- [ ] Domain is either Vercel/Netlify default (.vercel.app / .netlify.app) OR you have a domain ready
- [ ] Scorecard composite was 90+

---

## Custom domain (once MVP is working)

### Vercel
1. Your project → Settings → Domains
2. Add `yourdomain.com`
3. Vercel shows DNS records to add (A + CNAME)
4. Update DNS at your registrar (Namecheap, GoDaddy, Cloudflare, etc.)
5. Wait ~15 min for DNS propagation
6. Vercel auto-issues SSL cert

### Netlify
Same flow: Site → Domain management → Add custom domain.

---

## What can go wrong

| Symptom | Fix |
|---------|-----|
| Build fails on Vercel/Netlify but works locally | Check Node version (Vercel default might differ). Pin Node version in `.nvmrc` or Vercel project settings. |
| `process.env.XXX is undefined` on server | Env var not set in Vercel/Netlify dashboard. Or it has `NEXT_PUBLIC_` prefix when it shouldn't. |
| Page is 404 after deploy | Next.js: check you didn't delete `pages/` or `app/`. Static: check publish directory is right. |
| SSL cert not issuing | DNS propagation not complete. Wait 15-30 min. Or check if your registrar has CAA records blocking Let's Encrypt. |
| Build is slow | Check you're not shipping `node_modules/` or giant images. |

---

## After deploy

1. **Smoke test:** visit the live URL, walk through your main flow
2. **Check mobile:** open on your phone OR Chrome DevTools device mode
3. **Arabic RTL:** if your ICP is MENA, verify RTL renders
4. **Lighthouse:** open DevTools → Lighthouse → run. Target 90+ for Performance, Accessibility, Best Practices
5. **Save your deploy record:** `docs/deployments/YYYY-MM-DD-v<version>.md` with: URL, git SHA, what changed

---

## Monitoring (free tiers)

- **Uptime:** uptimerobot.com (free) — pings your URL every 5 min, alerts on downtime
- **Errors:** Sentry free tier (5K events/month) — catches exceptions
- **Analytics:** PostHog free tier, or Plausible, or Vercel Analytics

Wire these on day one. Don't wait until your first incident.

---

## Rollback

**Vercel:** Project → Deployments → find the last working one → click "Promote to production"
**Netlify:** Deploys → find the good one → click "Publish deploy"

Either platform lets you roll back in under 30 seconds. Do not edit files on the production server (there isn't one — it's serverless).
