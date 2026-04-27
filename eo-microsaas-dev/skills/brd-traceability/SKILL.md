# brd-traceability — BRD ↔ Test Mapping

**Purpose:** Every Business Requirements Document acceptance criterion has a tagged test. Nothing ships without traceability.

**Pillar:** Boris #4 — Verification Before Done + EO-Brain integration
**Time cost:** 5-10 minutes per BRD at start of sprint. Zero cost at PR time (just grep).

---

## The contract

Every BRD lives at `architecture/brd.md` (or `docs/brd.md`). Every user story has numbered acceptance criteria. Every AC has a test tagged `@AC-{story}.{criterion}`.

### BRD format (required)

```markdown
## Story 1: Password Reset

**As a** logged-out founder
**I want to** reset my password via email
**So that** I can regain access if I forget it

### Acceptance Criteria
- **AC-1.1** User enters email, receives reset link within 60 seconds
- **AC-1.2** Link expires after 1 hour
- **AC-1.3** Password must be ≥8 chars with 1 number
- **AC-1.4** Success page shows login CTA
```

### Test tagging (required)

```ts
// tests/auth/password-reset.test.ts
describe('Password Reset', () => {
  it('sends reset email within 60s @AC-1.1', async () => { ... });
  it('expires link after 1 hour @AC-1.2', async () => { ... });
  it('enforces password strength @AC-1.3', async () => { ... });
  it('redirects to login on success @AC-1.4', async () => { ... });
});
```

---

## The traceability check

Run before every PR that claims to "complete" a BRD story:

```bash
# For each AC-N.N in the BRD, find matching test
grep -oE "AC-[0-9]+\.[0-9]+" architecture/brd.md | sort -u > /tmp/brd-acs.txt
grep -orE "@AC-[0-9]+\.[0-9]+" tests/ | grep -oE "AC-[0-9]+\.[0-9]+" | sort -u > /tmp/test-acs.txt

echo "=== ACs in BRD but no test ==="
comm -23 /tmp/brd-acs.txt /tmp/test-acs.txt

echo "=== Tests tagged but no BRD AC ==="
comm -13 /tmp/brd-acs.txt /tmp/test-acs.txt
```

**Decision rules:**
- Any AC missing a test → Engineering hat Q2 caps at 6
- Any test tagged with non-existent AC → rename test or update BRD
- 100% mapped → Engineering hat Q2 can reach 10

---

## Coverage target

| Sprint phase | Minimum coverage |
|--------------|------------------|
| Spike / prototype | 50% (happy path only) |
| Feature complete | 90% (happy + error) |
| Pre-ship | 100% (all ACs mapped) |

---

## When BRD doesn't exist

If `architecture/brd.md` is missing for the feature being built:

1. **Stop coding.** Return to EO-Brain Phase 4 (Architecture) or Phase 1 (ProjectBrain).
2. **Write a 1-page mini-BRD** at minimum:
   - User story (3 lines)
   - 3-5 acceptance criteria
   - Out-of-scope list
3. **Commit BRD before any test/code.**

Shipping without a BRD forces Product hat ≤ 4 (see product-hat.md red flags).

---

## Integration with EO-Brain

EO-Brain Phase 4 (Architecture) produces the BRD. The `handover-bridge` skill converts EO-Brain output → Claude Code starter:
- BRD copied to `architecture/brd.md`
- Placeholder tests generated with `@AC-N.N` tags + `.skip` stubs
- First PR implements the ACs one by one, un-skipping tests

---

## Enforcement

- **eo-scorer Engineering hat Q2** runs the traceability grep
- **/7-eo-ship** blocks merge if coverage < 90%
- **/8-eo-retro** reports AC coverage trend week-over-week

---

## Examples

### Good — complete traceability

```
BRD: 12 ACs
Tests tagged: 12 @AC refs
Coverage: 100% → Engineering hat Q2 = 10
```

### Bad — missing tests

```
BRD: 12 ACs
Tests tagged: 7 @AC refs
Missing: AC-2.3, AC-2.4, AC-3.1, AC-4.2, AC-5.1
Coverage: 58% → Engineering hat Q2 = 4, PR blocked
```

### Bad — drift

```
BRD: 8 ACs (older)
Tests tagged: 11 @AC refs (newer, includes AC-9.1 that's not in BRD)
Action: Update BRD to include AC-9.1 or remove test
```

---

## Anti-patterns

- **Tagging after-the-fact to pass the check:** Tests should be written DURING development, not retrofit. Re-score honestly.
- **Vague ACs:** "Login works" is not testable. Rewrite to "User with valid credentials lands on /dashboard within 2s".
- **One test covering 5 ACs:** Each AC needs its own `it()` block. Otherwise failure granularity is lost.
