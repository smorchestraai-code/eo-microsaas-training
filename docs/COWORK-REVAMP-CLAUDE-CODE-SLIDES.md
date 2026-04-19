# Cowork Revamp Guide — EO-05-ClaudeCode Slides

**For:** Cowork team maintaining `01-Training-Content/EO-05-ClaudeCode/`
**From:** SMOrchestra / EO team
**Date:** 2026-04-19
**Scope:** `EO-Slides-05-ClaudeCode-v2.pptx` (27 slides) + `EO-Slides-05-Code-Closing.pptx`
**Why:** The new `eo-microsaas-dev` Claude Code plugin (v1.0.0-pilot) shipped. Slides reference older tooling and miss the 7-pillar workflow + 5-hat gate that students will actually use.

---

## Context in 60 seconds

Module EO-05 teaches students how to move from EO-Brain output → shipped MVP using Claude Code. We just released a dedicated plugin that codifies the workflow into 8 slash commands (`/eo-plan`, `/eo-code`, `/eo-review`, `/eo-score`, `/eo-bridge-gaps`, `/eo-ship`, `/eo-debug`, `/eo-retro`) plus 7 skills.

The current slides (v2, 27 slides) predate the plugin. Students now have a concrete toolbar — the slides should teach that toolbar, not generic "use Claude Code" advice.

**Plugin source + docs:** `github.com/smorchestraai-code/eo-microsaas-training/tree/main/eo-microsaas-dev`

---

## Slide-by-slide revamp matrix

This is a directional map, not a script. Use your build_deck.js to regenerate after edits.

### Keep (mostly unchanged)
| Slides | Reason |
|--------|--------|
| Intro / opener | Module welcome, keep |
| "What is Claude Code" | Foundational, keep current explanation |
| IDE setup / install basics | Still correct (install.sh handles it) |
| Closing deck | Keep as-is unless explicit workflow mismatch |

### Replace entirely

| Current theme | New theme | Why |
|---------------|-----------|-----|
| Generic "prompt Claude Code to build" | **The 7-pillar workflow** (Boris + gstack + superpowers + EO additions) | Students now have the pillars named; anchor the mental model. |
| Ad-hoc QA advice | **5-hat scoring gate (90+ to ship)** — one slide per hat (Product, Architecture, Engineering, QA, UX) | The quality gate IS the workflow. Five focused slides > one vague one. |
| "Use Claude Code to debug" | **/eo-debug and Boris's autonomous bug fixing** | Teach the specific command + protocol (hypothesis → evidence → root cause → regression test). |
| "Remember what Claude Code did" | **Self-improvement loop via .claude/lessons.md** | The biggest compounding lever. One slide on the lessons file + SessionStart hook. |
| Generic "be careful with AI" | **The elegance pause** — 3 questions, commit block template | Boris's pillar #5. Concrete, not philosophical. |

### Add (new slides)

| New slide | Position | Content |
|-----------|----------|---------|
| **The 8 slash commands** | Early (after intro) | Visual table: command → what it does → when to run. One glance, full picture. |
| **Daily command chain** | After 8-commands | Flowchart: `/eo-plan` → `/eo-code` → `/eo-review` → `/eo-score` → `/eo-bridge-gaps` (if <90) → `/eo-ship` → `/eo-retro` (weekly) |
| **The handover-bridge moment** | After EO-Brain recap | "What happens when you leave EO-Brain and open Claude Code" — the bootstrap prompt + `handover-bridge` skill |
| **MENA auto-checks** | Late (before wrap) | `arabic-rtl-checker` (8 points), `mena-mobile-check` (10 points) — explain the cap at 6 if RTL/mobile untested |
| **BRD traceability** | Mid (during coding flow) | `@AC-N.N` tagging → test tagging → grep coverage. Concrete example from calibration-examples.md |
| **Score inflation warning** | Near end | Show the real example: plugin was built, self-scored 95, reality was 60. Honest scoring is the whole point. |
| **Pilot expectations** | Penultimate | You're in the first cohort. Expect bugs. File issues. `eo-microsaas-dev` v1.0.0-pilot → v1.1 based on your feedback. |

### Remove

| Current slide content | Why remove |
|-----------------------|------------|
| Any mention of `smorch-dev-scoring` | Internal, not for students. Replaced by eo-scorer skill. |
| Any generic "best practices" slides without a command mapping | If it doesn't map to a slash command or a rubric, it's noise. |
| Outdated tool screenshots (pre-v2 Claude Code UI) | Replace with fresh screenshots from current CLI + the plugin loaded |
| Long "philosophy of AI coding" slides | Replace with the 7 pillars (each 1 line). Philosophy compressed. |

---

## Visual guidelines

### Color / branding
- Match existing EO palette (orange primary, white, gray accents — AppSumo-inspired)
- New accent for "commands": monospace background with the slash command in orange
- Score gate visual: use a speedometer or horizontal bar (0-100) with 90 marked in green, 80-89 yellow, <80 red

### Screenshots needed (before regenerating deck)
1. Claude Code session with `/eo` autocomplete popup visible (all 8 commands)
2. A real score report (use the one we generated at composite 82 as the honest example)
3. `.claude/lessons.md` file in an editor (5-10 lines visible)
4. Arabic RTL component side-by-side with LTR (375px viewport, phone frame)
5. git log showing elegance pause commit block

Ask Mamoun for these — he'll capture them during the pilot week with real student PRs.

### Arabic slides
If this module has an Arabic version:
- All command names stay English (`/eo-plan`, not a transliteration)
- Pillar titles: bilingual — English technical term + Arabic explanation
- Example: "Elegance Pause / توقف الأناقة — اسأل نفسك: في طريقة أبسط؟"

---

## Script / presenter notes to update

Location: `EO-05-ClaudeCode/build_deck.js` likely has presenter notes embedded per slide.

### Presenter note changes

| Old note pattern | New note pattern |
|------------------|------------------|
| "Show students how Claude Code helps" | "Show students THE 8 COMMANDS. Run `/eo-plan` live in a demo project." |
| "Explain Claude Code is AI for coding" | "Explain the 7 pillars in 60 seconds. Anchor: Plan → Subagents → Lessons → Verify → Elegance → Bugs → Score." |
| "Students should test their work" | "Students run `/eo-score`. 90+ or they don't ship. Show the trend.csv over 3 PRs." |

### Live demo segment (add if missing)

Slides alone won't land this. Add a 10-minute live demo block:

```
Demo flow (do this live, on a student's laptop if possible):
1. Open a new project directory
2. Show bootstrap prompt → handover-bridge runs → project scaffolds
3. Run /eo-plan with a toy feature ("add a testimonial carousel")
4. Approve plan → /eo-code writes a red test, then green impl
5. /eo-review runs, shows the punch list
6. /eo-score → 85 composite
7. /eo-bridge-gaps → lifts UX hat from 7 to 9
8. /eo-ship → PR created with score report body
Total: ~10 minutes. Single best teaching moment in the module.
```

---

## Build + QA flow for the revamped deck

1. **Edit** `build_deck.js` to reflect new content
2. **Regenerate** pptx: `node build_deck.js` (or your current build command)
3. **Export** to PDF: keep the qa/ folder convention (slide-01.jpg ... slide-NN.jpg)
4. **Self-review:** one pass for typos, one pass for command accuracy (copy-paste the command into Claude Code to verify it resolves)
5. **Pilot feedback:** ship to pilot cohort as v3-draft; collect feedback in week 1; final v3 after pilot

---

## What's already in place vs what's new

### Already in the slides (keep)
- Claude Code install explanation
- Introduction to Claude Code as a tool
- Closing encouragement deck

### Net-new in the revamp
- 7 pillars
- 8 slash commands (table + chain)
- 5-hat scoring gate (5 focused slides)
- `.claude/lessons.md` self-improvement
- Elegance pause (3 questions + commit block)
- `handover-bridge` moment
- MENA auto-checks (Arabic RTL, mobile 375px)
- BRD traceability (@AC-N.N tagging)
- Score inflation warning (honest calibration)
- Live demo block (10 minutes)
- Pilot expectations

### Removed
- `smorch-dev-scoring` references
- Generic "best practices"
- Philosophy-heavy slides without command mapping

---

## Estimated effort

| Task | Hours |
|------|-------|
| Read plugin docs + understand workflow | 2 |
| Edit build_deck.js script content | 4 |
| Capture fresh screenshots (needs Mamoun) | 2 |
| Regenerate + QA | 2 |
| Live demo rehearsal | 2 |
| Arabic translation (if bilingual) | 4 |
| **Total (English only)** | **~12 hours** |
| **Total (bilingual)** | **~16 hours** |

---

## Files cowork will touch

```
01-Training-Content/EO-05-ClaudeCode/
  build_deck.js                          ← edit content + structure
  EO-Slides-05-ClaudeCode-v2.pptx        ← regenerate → v3
  EO-Slides-05-Code-Closing.pptx         ← light edit (reference plugin)
  qa/                                    ← regenerate screenshots after build
  qa2/                                   ← reconcile or delete (duplicates)
```

**Side note:** `qa/` and `qa2/` both contain slide-NN.jpg exports. Recommend collapsing to single `qa/` folder during this revamp to reduce confusion.

---

## Questions for cowork before starting

1. Is `build_deck.js` the authoritative source, or does someone edit the pptx directly? (confirms single source of truth)
2. Who owns the Arabic translation — in-house or external translator?
3. Is there an existing slide-review checklist we should follow?
4. What's the deadline — tied to a cohort start date?

---

## Contact

Ping Mamoun in the EO cowork Slack. He'll provide:
- Fresh screenshots during pilot week
- Live demo script rehearsal
- Reviews of the v3-draft before it goes to cohort
