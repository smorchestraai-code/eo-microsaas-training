# PAYMENT-PROVIDER-SWAPS.md — per-provider scaffold diff

**Status:** living doc.
**Read by:** `eo-dev-start` (Step 8b — resolve `payment_provider`), `handover-bridge` (Step 4 — scaffold the right lib), `eo-dev-plan` (plans that touch payment).
**Rule:** EO projects are **never Stripe-only**. MENA ICPs get a Gulf-native provider by default.

---

## Provider matrix

| Provider | Primary region | Currencies | Mada / local rails | Arabic checkout | SDK quality (2026-Q2) |
|----------|----------------|-----------|--------------------|------------------|------------------------|
| **Tap Payments** | UAE, KSA, Kuwait, Bahrain, Qatar, Oman | AED, SAR, KWD, BHD, QAR, OMR, USD | ✅ Mada, KNET, Benefit, Naps | ✅ | good |
| **HyperPay** | KSA (Mada-first), Egypt, UAE | SAR, EGP, AED, USD | ✅ Mada, Meeza | ✅ | good |
| **Moyasar** | KSA | SAR, USD | ✅ Mada, Apple Pay | ✅ | good |
| **PayTabs** | UAE, KSA, Egypt, Jordan, Oman, Kuwait | AED, SAR, EGP, JOD, OMR, KWD, USD | ✅ multiple local rails | ✅ | OK |
| **Stripe** | Global (limited MENA coverage) | USD, EUR, AED (limited) | ❌ no Mada | limited | excellent |

---

## How Claude resolves `payment_provider` in Step 8b

1. **BRD explicit** — BRD or tech-stack-decision names a provider → use it.
2. **MENA + silent** — `mena_flag=true` and BRD does not name a provider → **Tap** (Gulf default).
3. **KSA-only + silent** — BRD says "KSA-only" or lists only SAR → **HyperPay** (Mada-first).
4. **Global or non-MENA + silent** — `payment_provider=stripe`.
5. **Multi-provider** — BRD names more than one (e.g. "Tap primary + HyperPay KSA + Stripe intl") → record all three; `payment_provider=<primary>`, scaffold primary now, list the others as follow-up stories.

No interactive question. Claude reads, picks, writes to `tech-stack-decision.md`, moves on.

---

## Per-provider scaffold (what `handover-bridge` installs in M1/M2/M3)

Each provider has its own thin wrapper at `src/lib/payment/<provider>/`. The shape is identical across providers so swapping later is one import change.

### Common interface (all providers implement)

```ts
// src/lib/payment/types.ts
export interface PaymentProvider {
  createCheckout(input: CheckoutInput): Promise<CheckoutResponse>;
  verifyWebhook(payload: string, signature: string): Promise<WebhookEvent>;
  refund(chargeId: string, amount?: number): Promise<RefundResponse>;
}
```

### Stripe — `src/lib/payment/stripe/`
- Deps: `stripe`
- Env: `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY`
- Webhook route: `src/app/api/webhooks/stripe/route.ts`

### Tap — `src/lib/payment/tap/`
- Deps: `axios` (Tap's SDK is REST-first)
- Env: `TAP_SECRET_KEY`, `TAP_PUBLIC_KEY`, `TAP_WEBHOOK_SECRET`
- Webhook route: `src/app/api/webhooks/tap/route.ts`
- Notes: Tap HPP (hosted payment page) is the default — no PCI scope.

### HyperPay — `src/lib/payment/hyperpay/`
- Deps: `axios`
- Env: `HYPERPAY_ENTITY_ID_MADA`, `HYPERPAY_ENTITY_ID_CREDIT`, `HYPERPAY_ACCESS_TOKEN`
- Webhook route: `src/app/api/webhooks/hyperpay/route.ts`
- Notes: two entity IDs — one for Mada, one for Visa/Mastercard. Scaffold both.

### Moyasar — `src/lib/payment/moyasar/`
- Deps: `axios`
- Env: `MOYASAR_SECRET_KEY`, `MOYASAR_PUBLISHABLE_KEY`
- Webhook route: `src/app/api/webhooks/moyasar/route.ts`

### PayTabs — `src/lib/payment/paytabs/`
- Deps: `axios`
- Env: `PAYTABS_PROFILE_ID`, `PAYTABS_SERVER_KEY`, `PAYTABS_REGION` (ARE/SAU/EGY/…)
- Webhook route: `src/app/api/webhooks/paytabs/route.ts`

---

## Fallback / multi-provider pattern

When BRD names a primary + fallback (common for MENA projects wanting international reach):

```ts
// src/lib/payment/index.ts
import { tap } from './tap';
import { stripe } from './stripe';

export function pickProvider(country: string): PaymentProvider {
  if (['AE', 'SA', 'KW', 'BH', 'QA', 'OM'].includes(country)) return tap;
  return stripe;
}
```

`handover-bridge` scaffolds this router when `payment_provider` is multi-valued.

---

## Testing scaffold

Every provider ships with:
- A placeholder test at `tests/payment-<provider>.test.ts` tagged `@AC-<story>.<n>` against the BRD's payment AC.
- A webhook-signature-verification unit test (security-critical; the QA hat Q4 checks this).

---

## Anti-patterns

- **Stripe-only in MENA** — instant AC failure. Mada is the dominant card rail in KSA.
- **Asking the founder which provider** — BRD already answered, or Step 8b resolves via MENA default. No interview.
- **Putting API keys in `.env.example`** — placeholders only. Never real keys.
- **Skipping webhook signature verification** — security-critical. Scaffold includes it by default.
