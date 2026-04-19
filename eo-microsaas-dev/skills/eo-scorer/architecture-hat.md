# Architecture Hat — Scoring Rubric

**Dimension:** Is the code organized in a way that scales? Can someone else read and extend it?

**Time to score:** 1-2 minutes per PR

---

## 8 Questions (each 1-10)

### 1. Logical modules
- ✅ 10: Each file has a single clear responsibility. Folder structure obvious.
- ⚠️ 7: Mostly clean, 1 file doing too much
- ❌ 4: Multiple files with overlapping responsibilities
- 💀 1: One giant file that does everything

### 2. Data flow explainable in 2 sentences
- ✅ 10: You can say "user submits form → X validates → Y writes DB → Z sends email" in one breath
- ⚠️ 7: Needs 3-4 sentences + a diagram
- ❌ 4: You have to trace through the code to understand
- 💀 1: Spaghetti — no clear flow

### 3. Separation of concerns (UI / logic / data)
- ✅ 10: React components = UI only. Hooks/utils = logic. Supabase client = data. Clean layers.
- ⚠️ 7: 90% clean, one leaky component with business logic
- ❌ 4: Mixed — DB calls inside components, fetch inside render
- 💀 1: Everything lives in one component

### 4. Data model sensible
- ✅ 10: Tables normalized (or deliberately denormalized with comment). RLS policies set. Foreign keys explicit.
- ⚠️ 7: Schema works but has 1 quirk (e.g., JSONB blob that should be a table)
- ❌ 4: Denormalization without reason, missing indexes, no RLS
- 💀 1: Schema is obviously wrong — bugs already surfaced

### 5. API surface minimal + RESTful-ish
- ✅ 10: Each endpoint does one thing. URL structure predictable. HTTP verbs correct.
- ⚠️ 7: Mostly clean, 1 endpoint doing too much
- ❌ 4: Multiple endpoints that should be one, or one endpoint doing 5 things
- 💀 1: RPC-style mess — endpoints named by action not resource

### 6. Subagents used for parallel exploration (Boris pillar 2)
- ✅ 10: For non-trivial research, you dispatched subagents (code search, spec read, etc.)
- ⚠️ 7: Mostly main-context, but used subagent for one task
- ❌ 4: All exploration in main context, context bloat
- 💀 1: No plan — ad-hoc exploration

### 7. Third-party dependencies justified
- ✅ 10: Each dep has a clear reason + you looked at the bundle size impact
- ⚠️ 7: Most deps justified, 1-2 unchecked
- ❌ 4: Added deps "just because" — bundle bigger without thought
- 💀 1: 5+ new deps for a small PR

### 8. Scalability risk identified
- ✅ 10: PR comment notes "at N users/rows, X will become the bottleneck"
- ⚠️ 7: Some thought given but not documented
- ❌ 4: Assumes current scale forever
- 💀 1: Already slow on sample data

---

## Scoring

**Average of 8 answers × 1.25** = Architecture hat (capped at 10)

## Red flags that force Architecture ≤ 6

- No types / strict mode off in TypeScript
- Database writes without RLS policies
- N+1 query patterns obvious on first read

## Red flags that force Architecture ≤ 3

- Credentials / API keys in code (not env)
- Schema migration breaking existing users' data
- API endpoints that bypass auth

## Calibration examples

See `calibration-examples.md`.
