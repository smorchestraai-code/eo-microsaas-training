---
name: eo-brain-ingester
description: "Resilient EO-Brain input parser. Single executable (parse.py) that ingests any EO-Brain folder shape — drifted BRD headers, missing files, partial content, Arabic or English, h2/h3 story headers, tagged or untagged carve, key:value or prose profile-settings — and returns a single canonical BrainStructure JSON. Hard-refuses ONLY on (a) EO-Brain dir missing or (b) BRD has zero AC-N.N tags. All other gaps surface as questions[] (blocking, founder must answer in plan-mode preview) or warnings[] (soft, proceed with default). Used by /1-eo-dev-start Step 7c, handover-bridge Step 4c, /eo-dev-repair."
version: "1.0"
---

# eo-brain-ingester — The Resilient Input Parser

**Pillar:** EO-specific — Postel's law for the v1.4.x bootstrap.
**Purpose:** Replace the brittle "regex-validates-then-rejects" pattern that v1.4.2 inherited. v1.4.3 ingests any reasonable EO-Brain shape, normalizes, surfaces gaps as questions for founder approval, and proceeds.

The single most important guarantee: **`/1-eo-dev-start` cannot fail on legitimate EO-Brain input.** This skill is the contract that delivers that.

---

## When to run

Three callers:

1. **`/1-eo-dev-start` Step 7c** — fresh-project bootstrap. Parse → produce BrainStructure → drives plan-mode preview + scaffold parameters.
2. **`handover-bridge` Step 4c** — during scaffold execution. Consume BrainStructure (no re-parse), use it to scaffold Files + write normalized BRD to `architecture/brd.md`.
3. **`/eo-dev-repair`** — when BRD or identity drift surfaces post-bootstrap. Re-ingest, re-surface questions, re-normalize.

Founders never call this skill directly. It runs underneath the numbered chain.

---

## The contract

### Implementation

```
skills/eo-brain-ingester/
├── SKILL.md           ← this file (the contract)
├── parse.py            ← the actual parser (Python 3.x, stdlib-only)
└── fixtures/           ← 5+ EO-Brain test folders (canonical, h2-tagged, h3-untagged, missing-identity, genuinely-empty)
```

### Invocation

```bash
python3 skills/eo-brain-ingester/parse.py <eo_brain_path> --pretty
```

Returns JSON `BrainStructure` to stdout. Exit 0 = success, exit 2 = refused.

### Self-test

```bash
python3 skills/eo-brain-ingester/parse.py --self-test
```

Iterates every fixture in `fixtures/`. Asserts: every `*-tagged` and `*-untagged` and `missing-*` fixture parses without refusal; every `genuinely-empty` and `*-missing` fixture refuses cleanly.

---

## The BrainStructure JSON shape

```yaml
schema_version: "1.0"
ingester_version: "1.0"
ingested_at: "2026-04-28T13:26:59Z"
eo_brain_path: "/abs/path/to/EO-Brain"

language:
  lang: "ar"                              # "ar" | "en"
  source: "_language-pref.md"             # | "inferred-from-brd" | "default"

identity:
  project_name: "EO Oasis MENA"
  project_name_source: "profile-settings.md (prose: 'Founder of EO Oasis MENA')"
  founder_name: "Mamoun Alamouri"
  founder_name_source: "profile-settings.md (prose under IDENTITY)"
  founder_email: "mamoun.alamouri99@gmail.com"
  icp_summary: "Solo Arabic-speaking technical founders (25-40)..."
  voice_notes:
    - "Gulf conversational tone"
    - "Banned buzzword: leverage"

stack:
  frontend: "Next.js 14 + TypeScript + Tailwind"
  backend: "Next.js API Routes"
  db: "Postgres (Supabase managed)"
  auth: "Supabase Auth"
  payments: ["Tap", "HyperPay", "Stripe"]
  deploy_lane: "Contabo"
  mena: true
  rtl: true
  source: "/abs/path/to/4-Architecture/tech-stack-decision.md"

bootstrap_prompt:                          # null if missing
  path: "/abs/path/to/5-CodeHandover/README.md"
  length_bytes: 12510

ux_artifacts:
  paths: [...]
  count: 3

brd:
  source_path: "/abs/path/to/4-Architecture/brd.md"
  source_checksum_sha256: "815fcc..."     # used to verify untouched after normalization
  total_acs: 60
  story_count: 6
  stories:
    - number: 1
      title: "Founder Account Registration + 2FA"
      title_source: "h3-header"            # h2-header | h3-header | h4-header | no-header | arabic-title | inferred
      ac_count: 10
      ac_tags: ["AC-1.1", "AC-1.2", ...]
      carve_tag: null                      # "[@WeekendMVP]" | "[@Phase2]" | null
      carve_source: "missing"              # "parsed" | "missing"
      loop_tags: ["[loop:auth]", "[loop:notify]"]
      loop_source: "inferred"              # "parsed" | "inferred"
    - ...
  scope_shape: "binary"                    # "canonical" | "binary" | "none"
  carve_state: "untagged"                  # "canonical" | "partial" | "untagged"
  loop_state: "untagged"                   # "canonical" | "partial" | "untagged"
  proposed_carve:
    weekend_mvp: [1, 2, 3, 4]
    phase_2: [5, 6]
  loop_coverage:
    covered: ["auth", "compliance", "domain", "notify"]
    missing: ["deploy", "money", "observability"]
    complete: false
  normalization_plan:
    - "Will add carve tags ([@WeekendMVP] for [1,2,3,4], [@Phase2] for [5,6])"
    - "Will add loop tags inferred from content for 6 stories"
    - "Will inject canonical SCOPE block (current shape: binary)"

phases_present:
  phase_0_scorecards: true
  phase_1_project_brain: true
  phase_2_gtm: true
  phase_3_newskills: true
  phase_4_architecture: true
  phase_5_handover: true

warnings:                                  # soft — proceed with default
  - "icp_summary not found — UX hat will cap at 8..."

questions:                                 # BLOCKING — founder must answer in plan-mode preview
  - key: "carve_approval"
    blocking: true
    prompt: "BRD has 6 stories with no [@WeekendMVP]/[@Phase2] tags. Propose: stories [1,2,3,4] = MVP, [5,6] = v2. Approve?"
    default_suggestion: "y"
    default_source: "first 4 stories = MVP, rest = Phase2"
    proposed_carve: {weekend_mvp: [1,2,3,4], phase_2: [5,6]}

  - key: "loop_approval"
    blocking: true
    prompt: "Inferred loop tags for 6 stories from content keywords. Approve all (y) or override per story."
    default_suggestion: "y"
    default_source: "keyword-based content inference"
    proposed_loops: {1: ["[loop:auth]","[loop:notify]"], 2: [...], ...}

  - key: "mvp_loop_gap"
    blocking: true
    prompt: "Weekend MVP slice missing loops: [deploy, money, observability]. Options: (A) move Phase2 story up (B) accept gap (C) return to Cowork."
    default_suggestion: "A"
    default_source: "Phase2 stories that could fill the gap: [{story_number: 6, title: '...', covers: ['money']}]"
    missing_loops: ["deploy", "money", "observability"]
    promote_candidates: [...]

refused: false
```

---

## Hard-refuse contract (only TWO conditions)

```
refused: true
reason: "eo-brain-missing"     → EO-Brain dir does not exist
reason: "brd-empty"            → BRD has zero AC-N.N tags
```

Both refusals include `remediation` text pointing the founder back to Cowork.

For **all other** input shapes — proceed. The parser handles:

| Drift case | Behavior |
|---|---|
| BRD uses h3 instead of h2 headers | Parsed via header-pattern fallback chain |
| BRD missing carve tags `[@WeekendMVP]`/`[@Phase2]` | `carve_state: "untagged"`, `proposed_carve` filled, blocking question generated |
| BRD missing loop tags `[loop:X]` | Inferred from title + AC content (weighted scoring), blocking question generated |
| BRD missing `## SCOPE` block | `scope_shape: "binary"` or `"none"`, normalization plan injects canonical block |
| MVP slice missing loops (incomplete 7-loop coverage) | `loop_coverage.complete: false`, blocking question with options A/B/C |
| `profile-settings.md` is prose, not key:value | Extracts founder name + project name from prose under "IDENTITY" / "WHO I AM" markers |
| `profile-settings.md` missing entirely | Falls through to bootstrap-prompt → companyprofile → BRD `**Product:**` → positioning. If still empty → blocking question. |
| Founder name unrecoverable | Blocking question with git config suggestion |
| Project name unrecoverable | Blocking question (no default) |
| `_language-pref.md` missing | Auto-detects from BRD content (Arabic chars → `ar`) or defaults to `en` with warning |
| `tech-stack-decision.md` missing | Falls through to MENA-safe defaults (Next.js + Supabase + Tap + Contabo) |
| ICP file missing | Falls through to BRD `**Target Users:**` line; if still empty, soft warning (UX hat caps at 8) |
| UX artifacts missing | Soft warning, UX hat caps at 8 |
| Bootstrap prompt missing | Soft warning, falls through to phase-by-phase identity extraction |

---

## Self-score protocol

Run `python3 parse.py --self-test`. Asserts:

| # | Check |
|---|---|
| 1 | `canonical-h3-tagged` fixture parses, `carve_state == "canonical"`, `loop_state == "canonical"` |
| 2 | `h3-untagged` fixture parses, `carve_state == "untagged"`, generates blocking question |
| 3 | `h2-tagged` fixture parses (legacy headers handled), normalization_plan includes header rewrite |
| 4 | `genuinely-empty` fixture REFUSES with reason `brd-empty` |
| 5 | `missing-identity` fixture parses, generates blocking question for `founder_name` |
| 6 | Real EO-Brain at `10-EO-Brain-Starter-Kit Final/` parses cleanly with `Mamoun Alamouri` + `EO Oasis MENA` extracted |
| 7 | `--self-test` exit code is 0 (all passes) |

Threshold: 7/7. Any failure → fix parser before declaring done.

---

## How callers use this

### `/1-eo-dev-start` Step 7c

```bash
# Run the ingester
PARSE_OUT=$(python3 ${PLUGIN_PATH}/skills/eo-brain-ingester/parse.py "$EO_BRAIN" --pretty 2>&1)
EXIT=$?

# Refused? Surface and exit.
if [[ $EXIT -eq 2 ]]; then
  reason=$(echo "$PARSE_OUT" | jq -r '.reason')
  remediation=$(echo "$PARSE_OUT" | jq -r '.remediation')
  echo "❌ Cannot bootstrap: $reason"
  echo "   $remediation"
  exit 2
fi

# Otherwise: read identity, surface questions in plan-mode preview, ask founder.
project_name=$(echo "$PARSE_OUT" | jq -r '.identity.project_name')
question_count=$(echo "$PARSE_OUT" | jq '.questions | length')

# For each question, prompt founder. Store answers.
for i in $(seq 0 $((question_count-1))); do
  prompt=$(echo "$PARSE_OUT" | jq -r ".questions[$i].prompt")
  default=$(echo "$PARSE_OUT" | jq -r ".questions[$i].default_suggestion")
  echo "$prompt"
  echo "(default: $default — press Enter to accept, or type override)"
  read answer
  # Store answer in answers.json for handover-bridge to consume
done

# Continue to plan-mode preview with identity + answers.
```

### `handover-bridge` Step 4c

Consumes the same BrainStructure object (passed by `/1-eo-dev-start`, no re-parse). Uses it to scaffold + write normalized BRD to `architecture/brd.md`.

### `/eo-dev-repair`

Re-runs `parse.py` against current state. Surfaces any drift via questions[] / warnings[]. Founder approves; repair applies.

---

## Anti-patterns (don't do this)

- **Refusing on header depth.** v1.4.2 did this. v1.4.3 normalizes via header-pattern fallback chain.
- **Silently defaulting on missing identity.** Generates blocking question; founder explicitly approves the default or overrides.
- **Modifying the EO-Brain source.** Cowork stays the strategic source of truth. Dev plugin reads, never writes there. Checksum verified before/after.
- **Hardcoded story header regex.** Use AC-N.N tag clusters as the universal signal; titles via fallback chain.
- **Inference without surfacing.** Every inference goes into `proposed_*` fields of questions[], with override hooks.
- **Refusing on MVP loop gap.** Surface options (move story / accept gap / return to Cowork). Founder decides.
