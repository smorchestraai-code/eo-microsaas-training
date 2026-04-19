# Examples

Reference projects students can fork, clone, or learn from.

## Planned examples

| Example | Stack | Status | What it demonstrates |
|---------|-------|:------:|----------------------|
| mini-scorecard | Next.js 14 + Supabase | Planned | Lead-magnet scorecard with 5 questions, GHL email capture |
| arabic-landing-page | Next.js 14 + Tailwind RTL | Planned | Complete Arabic RTL layout with Cairo/Tajawal fonts |
| stripe-one-tier | Next.js 14 + Stripe | Planned | Single-tier subscription, webhook handling |
| static-playbook | Astro | Planned | Static content site with MDX, Netlify deploy |

## Structure per example

```
examples/NAME/
├── README.md              # What it demonstrates, how to run, what to learn
├── .env.example
├── package.json
└── ... (project files)
```

Each example is a complete, runnable project with its own BRD, tests, and deployment config.

## Contributing an example

See `CONTRIBUTING.md` in the repo root. Examples must:
- Include a BRD in `docs/BRD-*.md`
- Pass `npm run typecheck && npm run lint && npm run build`
- Have `@AC-*` tagged tests
- Score 90+ on the 5-question scorecard
