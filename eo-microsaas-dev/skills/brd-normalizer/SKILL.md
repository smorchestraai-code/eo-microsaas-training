---
name: brd-normalizer
description: "Resilient BRD parser + normalizer. Takes any BRD format the architect (4-eo-tech-architect) or a student might produce — h2 / h3 / h4 story headers, tagged or untagged, missing or partial SCOPE block, Arabic or English titles — and returns (a) a parsed canonical structure (story list with ACs + carve tags + loop tags) and (b) a normalized BRD file in v2.7.0 canonical format. Idempotent. Used by eo-dev-start Step 7c, handover-bridge Step 4c, eo-dev-repair. Hard-refuses only on: missing file or zero AC-N.N tags."
version: "1.0"
---

# brd-normalizer — The Resilient BRD Parser

**Pillar:** EO-specific — Postel's law for the v1.4.x bootstrap. Be liberal in what we accept, strict in what we produce.
**Purpose:** Transform any BRD shape (h2 / h3 / h4 headers, tagged or untagged, missing SCOPE block, Arabic or English) into canonical v2.7.0 format without rejecting the founder's work.

This skill replaces the brittle "regex-validates-then-rejects" pattern that v1.4.2 inherited. v1.4.3 ingests, normalizes, surfaces inferences for founder approval, and proceeds. The original EO-Brain BRD is **never** modified — normalization writes only to the project's `architecture/brd.md`.

---

## When to run

Called by three upstream consumers:

1. **`eo-dev-start` Step 7c** — during fresh-project bootstrap. Parse BRD → produce structured input for plan-mode preview + scaffold.
2. **`handover-bridge` Step 4c** — during scaffold execution. Read EO-Brain BRD → write normalized copy to `architecture/brd.md`.
3. **`eo-dev-repair`** — when BRD drift surfaces post-bootstrap (e.g., student edited `architecture/brd.md` and broke canonical format). Re-normalize in place.

Never invoked directly by a founder. Always callable as a sub-routine of one of the three above.

---

## The contract

### Input

A BRD file path. That's it. No assumptions about shape.

```
brd_normalizer.parse(brd_path) → BRDStructure | RefuseError
brd_normalizer.normalize(brd_structure, target_path) → write canonical BRD to target_path
```

### Output (BRDStructure object — passed back to caller)

```yaml
parsed:
  source_path: "$EO_BRAIN/4-Architecture/brd.md"
  total_acs: 60                        # count of unique AC-N.N tags
  story_count: 6                       # derived from unique AC story numbers (1-6)
  stories:
    - number: 1
      title: "Founder Account Registration + 2FA"
      title_source: "h3-header"        # h2-header | h3-header | h4-header | story-prefix | inferred
      ac_count: 10
      ac_tags: ["AC-1.1", "AC-1.2", ...]
      carve_tag: "[@WeekendMVP]"       # parsed if present, OR "inferred:WeekendMVP" if missing + auto-assigned
      loop_tags: ["[loop:auth]", "[loop:compliance]"]  # parsed OR inferred from content
    - number: 2
      ...
  has_scope_block: true                 # whether ## SCOPE block exists
  scope_block_shape: "binary"           # canonical (3 subsections) | binary (MVP + Out-of-Scope only) | none
  carve_state: "untagged"               # canonical | partial | untagged
  loop_state: "untagged"                # canonical | partial | untagged

normalization_plan:                     # what normalize() will do, surfaced to founder for approval
  - "Headers already h3 — no change"
  - "Will tag Stories 1-4 as [@WeekendMVP], Stories 5-6 as [@Phase2] (default for 6-story BRDs)"
  - "Will infer [loop:X] tags per story from title + ACs (see proposed_loops below)"
  - "Will replace binary SCOPE block with canonical 3-subsection (Weekend MVP / v2 Roadmap / Out of Scope)"

proposed_carve:                         # founder can override before scaffold writes
  weekend_mvp: [1, 2, 3, 4]
  phase_2: [5, 6]

proposed_loops:                         # founder can override before scaffold writes
  story_1: ["auth", "compliance"]       # signup + RLS in ACs → auth + compliance
  story_2: ["domain", "notify"]         # form submission + WhatsApp confirm → domain + notify
  story_3: ["domain"]                   # admin dashboard → domain (no notify/money/deploy)
  story_4: ["money"]                    # tiered pricing + checkout → money
  story_5: []                           # phase 2, no inference
  story_6: []
```

### Hard-refuse conditions (only two)

```
RefuseError reason="brd-missing"       → file does not exist at brd_path
RefuseError reason="brd-empty"         → zero AC-N.N tags found in file content
```

For **all other** shapes — proceed. Normalize. Surface inferences. Let the founder approve.

---

## Step-by-step parse algorithm

### Step 1 — File existence

```bash
test -f "$brd_path" || refuse(reason="brd-missing", remediation="Run /4-eo-tech-architect in Cowork to generate the BRD.")
```

### Step 2 — Extract AC tags (the universal signal)

Story count comes from AC tag clusters, not header parsing. Every legitimate BRD has these.

```bash
# Extract every unique AC-N.N tag
ac_tags=$(grep -oE 'AC-[0-9]+\.[0-9]+' "$brd_path" | sort -u)

# Refuse if zero
[[ -z "$ac_tags" ]] && refuse(reason="brd-empty", remediation="BRD has no acceptance criteria. Finish 4-eo-tech-architect Phase 4, then re-run /1-eo-dev-start.")

# Story count = count of unique first-component values
story_numbers=$(echo "$ac_tags" | sed 's/AC-//;s/\..*//' | sort -un)
story_count=$(echo "$story_numbers" | wc -l)
```

**Output:** list of story numbers (e.g. `[1, 2, 3, 4, 5, 6]`).

### Step 3 — Extract story titles (header-agnostic, multi-pattern)

For each story number, find its title by trying patterns in order. First match wins.

```python
patterns = [
    r'^###\s+Story\s+{N}[:\s]+(.+?)$',          # canonical h3
    r'^##\s+Story\s+{N}[:\s]+(.+?)$',           # legacy h2
    r'^####+\s*Story\s+{N}[:\s]+(.+?)$',        # deeper
    r'^Story\s+{N}[:\s]+(.+?)$',                # no header at all
    r'^User Story\s+{N}[:\s]+(.+?)$',           # alt phrasing
    r'^قصَّة\s+{N}[:\s]+(.+?)$',                # Arabic
    r'^القصَّة\s+{N}[:\s]+(.+?)$',              # Arabic alt
]

for N in story_numbers:
    for pattern in patterns:
        match = grep(pattern.format(N=N), brd_path)
        if match:
            title = match.group(1).strip()
            title_source = pattern_label(pattern)
            break
    else:
        title = f"Story {N}"
        title_source = "inferred"
```

**Output:** title + `title_source` per story. `title_source` records which pattern matched (drives normalization decisions).

### Step 4 — Extract per-story AC count

```bash
for N in story_numbers:
    ac_count = $(grep -cE "AC-${N}\.[0-9]+" brd_path)
    # Warning (not refusal) if < 3
    if (( ac_count < 3 )):
        warnings.append(f"Story {N} has only {ac_count} ACs (canonical: ≥3)")
```

Per-story AC count <3 is a warning, not a refusal. The founder may have a 1-AC story for a deliberate reason. Surface in plan-mode preview, let them decide.

### Step 5 — Extract carve tags (`[@WeekendMVP]` / `[@Phase2]`)

```bash
for N in story_numbers:
    # Search the line(s) immediately around the story header
    carve = grep_in_story_block(N, r'\[@(WeekendMVP|Phase2)\]')
    if carve:
        carve_tag = f"[@{carve}]"
        carve_source = "parsed"
    else:
        carve_tag = None
        carve_source = "missing"
```

If **all stories** have carve tags → `carve_state = "canonical"`.
If **some stories** have carve tags → `carve_state = "partial"`.
If **no stories** have carve tags → `carve_state = "untagged"`. Triggers Step 8 inference.

### Step 6 — Extract loop tags (`[loop:auth]` etc.)

Same pattern as Step 5, looking for `[loop:(auth|domain|money|notify|deploy|observability|compliance)]`.

### Step 7 — Detect SCOPE block

Three shapes:

```bash
if grep -qE '^### Weekend MVP' brd_path && grep -qE '^### v2 Roadmap' brd_path:
    scope_shape = "canonical"
elif grep -qE '^## SCOPE' brd_path && grep -qE '^### .*MVP Scope|MVP|Out of Scope' brd_path:
    scope_shape = "binary"            # has SCOPE but not the 3-subsection canonical
else:
    scope_shape = "none"
```

### Step 8 — Inference engine (when tags missing)

#### 8a — Carve inference (when `carve_state ≠ canonical`)

Default rule:

```
if story_count <= 4:
    proposed_carve.weekend_mvp = all stories
    proposed_carve.phase_2 = []
elif story_count <= 7:
    proposed_carve.weekend_mvp = stories[1..4]
    proposed_carve.phase_2 = stories[5..N]
else:
    # 8+ stories — likely too ambitious for Weekend MVP, flag for founder
    proposed_carve.weekend_mvp = stories[1..4]
    proposed_carve.phase_2 = stories[5..N]
    warning: "Story count > 7. Confirm Weekend MVP is really stories 1-4, or override."
```

This is a default. Plan-mode preview surfaces it; founder overrides before scaffold writes.

#### 8b — Loop inference (when `loop_state ≠ canonical`)

Per-story content scan for the 7 loops. Score each loop based on keyword presence in the story's title + ACs.

```yaml
loop_keywords:
  auth: ["registration", "register", "signup", "sign-up", "sign up", "login", "log in", "OTP", "2FA", "password", "session", "auth", "تسجيل", "دخول"]
  domain: ["dashboard", "submit", "list", "create", "edit", "view", "search", "filter", "browse", "directory", "catalog"]
  money: ["pricing", "tier", "checkout", "payment", "subscribe", "subscription", "Tap", "HyperPay", "Stripe", "Moyasar", "PayTabs", "webhook", "billing", "دفع", "اشتراك"]
  notify: ["email", "WhatsApp", "SMS", "notification", "Resend", "Unifonic", "Twilio", "GHL", "send", "notify", "message"]
  deploy: ["deploy", "subdomain", "SSL", "DNS", "/api/health", "production", "Contabo", "VPS", "Vercel"]
  observability: ["Sentry", "PostHog", "uptime", "monitor", "analytics", "logging", "metric"]
  compliance: ["RLS", "row-level security", "policy", "PDPL", "GDPR", "data residency", "audit log", "secret", "encrypt"]

# For each story, count keyword matches per loop
# Loops with ≥1 match → assigned to that story
# A story can have multiple loops (most do)
```

Surface to founder in plan-mode preview:

```
🔧 Loop tag inference (founder confirms):

  Story 1 — Founder Account Registration + 2FA
    Title + ACs match: "registration" "OTP" "2FA" "password" "session" "RLS"
    → [loop:auth] [loop:compliance]
    Override? (default = accept)

  Story 2 — Founder Submission Flow
    Title + ACs match: "submit" "form" "save" "WhatsApp" "Resend"
    → [loop:domain] [loop:notify]
    Override? (default = accept)

  ... (one block per story)
```

Founder presses `y` to accept all, or specifies overrides per story. Skill records final loop assignments.

#### 8c — Loop coverage check (Weekend MVP only)

After inference, the 4 (or fewer) `[@WeekendMVP]` stories collectively must cover all 7 loops. If any loop is missing across the MVP slice:

```
⚠️ Loop coverage gap: [loop:money] not assigned to any [@WeekendMVP] story.
  Options:
    A. Move Story 4 (currently [@Phase2], has "pricing" keywords) into [@WeekendMVP]
    B. Add a new MVP story for money (return to Cowork to refine BRD)
    C. Proceed with gap (NOT RECOMMENDED — Weekend MVP would ship without monetization)
```

Founder picks A/B/C in plan mode. Default suggestion is A when an obvious candidate exists.

---

## Normalize algorithm

After parsing succeeds and the founder approves the proposed normalization plan, write the canonical BRD:

### Step N1 — Read source

```bash
content = read_file(brd_path)
```

### Step N2 — Rewrite story headers to canonical h3

For each story header found in Step 3 (any pattern), rewrite to:

```
### Story {N} [@{CarveTag}] [loop:{loop1}] [loop:{loop2}] ... : {Title}
```

Example:
- Before: `### Story 1: Founder Account Registration + 2FA`
- After: `### Story 1 [@WeekendMVP] [loop:auth] [loop:compliance]: Founder Account Registration + 2FA`

If headers are h2 → rewrite to h3 (`##` → `###`).
If header was missing entirely (Step 3 fell to "inferred") → insert a fresh h3 header.

### Step N3 — Inject canonical SCOPE block (if missing)

If `scope_shape ≠ "canonical"`:

Replace existing SCOPE block (or insert one above `## USER STORIES`) with the canonical 3-subsection format from `4-eo-tech-architect/references/brd-template.md`.

The Weekend MVP block lists `[@WeekendMVP]` story numbers; the v2 Roadmap block lists `[@Phase2]` story numbers; the Out of Scope block carries any pre-existing exclusion content if present, or starts empty with a placeholder ("To be defined — capture explicit non-goals here").

### Step N4 — Add normalization comment header

At the top of the normalized BRD, insert:

```markdown
<!-- BRD normalized by eo-microsaas-dev brd-normalizer v1.0 on {DATE}.
     Original source: {EO_BRAIN_PATH}/4-Architecture/brd.md (untouched).
     Normalization actions:
       - {action 1}
       - {action 2}
       - ...
     To re-normalize after manual edits: /eo-dev-repair -->
```

This makes the normalization auditable and re-runnable.

### Step N5 — Write to target

```bash
write_file(target_path, normalized_content)
```

`target_path` is the project's `architecture/brd.md`. The EO-Brain source is **never** written to.

### Step N6 — Verify

```bash
# Re-parse the just-written file
re_parsed = parse(target_path)

# Sanity checks
assert re_parsed.story_count == parsed.story_count, "story count drift during normalization"
assert re_parsed.total_acs == parsed.total_acs, "AC tag drift during normalization"
assert re_parsed.carve_state == "canonical", "normalize failed to produce canonical carve"
assert re_parsed.loop_state == "canonical" OR all_phase2_stories, "normalize failed to produce canonical loops"
```

If any assertion fails → roll back the write, refuse with diagnostic.

---

## Idempotency contract

Running `normalize()` twice on the same BRD produces byte-identical output (after the second run). This is critical for `eo-dev-repair` — re-running the normalizer must be safe.

Test: every fixture BRD in `skills/eo-dev-start/fixtures/` is normalized, then normalized again. Diff must be empty.

---

## Anti-patterns (don't do this)

- **Refusing on header depth.** v1.4.2 did this. v1.4.3 normalizes.
- **Modifying the EO-Brain source.** Cowork is the strategic source of truth. Dev plugin reads, never writes there.
- **Inferring carve tags silently.** Inference is fine. Hiding it from the founder is not. Surface in plan-mode preview, accept overrides.
- **Hard-refusing when MVP is missing a loop.** Surface with options (move story, add story, proceed with gap). Founder decides.
- **Using header text as the source of story count.** ALWAYS use AC-N.N tag clusters. They're the universal signal.

---

## Test fixtures (in `skills/eo-dev-start/fixtures/`)

Six BRDs, covering every shape:

1. `brd-canonical-h3-tagged.md` — perfect input. parse → no normalization needed.
2. `brd-h2-tagged.md` — legacy h2 headers, tagged. parse → normalize headers only.
3. `brd-h3-untagged.md` — current architect output (the bug case). parse → normalize tags.
4. `brd-mixed-headers.md` — h2 + h3 mixed. parse → normalize headers.
5. `brd-no-scope-block.md` — missing `## SCOPE`. parse → inject canonical SCOPE.
6. `brd-genuinely-empty.md` — zero ACs. parse → REFUSE (the only refusal case).

Plus the user's actual BRD at `10-EO-Brain-Starter-Kit Final/EO-Brain/4-Architecture/brd.md` — used as the ground-truth smoke test.

---

## Self-score protocol

After parse + normalize, verify:

| # | Check |
|---|---|
| 1 | Source file existed and was readable |
| 2 | AC-N.N tag count > 0 (else refuse) |
| 3 | Every detected story has a non-empty title |
| 4 | Carve plan covers all stories (every story has [@WeekendMVP] or [@Phase2]) |
| 5 | Loop plan covers every [@WeekendMVP] story with ≥1 loop tag |
| 6 | Weekend MVP slice collectively covers all 7 loops (or founder accepted gap) |
| 7 | EO-Brain source file unchanged (checksum match before/after) |
| 8 | Normalized output re-parses to canonical state |
| 9 | Idempotency: normalize(normalize(x)) == normalize(x) |
| 10 | All 6 fixtures + user's BRD pass parse without refusal |

Threshold: 10/10 on every run. Any failure → roll back, refuse with diagnostic.
