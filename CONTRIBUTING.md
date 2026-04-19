# Contributing

This repo is maintained by SMOrchestra for EO MicroSaaS students. If you're a student, teaching assistant, or collaborator and you want to add content — here's how.

## Who can contribute

- **Mamoun / core SMOrchestra team:** direct push to `main` for minor updates; PR for breaking changes
- **Teaching assistants / course authors:** PRs welcome for new courses + examples
- **Students:** open issues for bugs, suggestions; PRs for fixes only (typos, broken links, outdated commands)

## What counts as content

| Type | Where | Complexity |
|------|-------|:----------:|
| SOP (procedure) | `sops/SOP-Name.md` | Low |
| Template (fill-in) | `templates/NAME-TEMPLATE.md` | Low |
| Reference doc | `reference/NAME.md` | Low |
| Course module | `courses/NN-name/` | High |
| Example project | `examples/name/` | Medium |
| CLAUDE.md updates | `CLAUDE.md` | Medium — requires testing |
| Hook changes | `settings.json` | High — requires end-to-end verification |
| install.sh changes | `install.sh` | High — requires fresh-machine test |

## Workflow

### For a new SOP, template, or reference doc (low complexity)

1. Fork + branch: `feat/sop-my-new-procedure`
2. Create file following naming convention (`SOP-Name.md`, `NAME-TEMPLATE.md`)
3. Follow the structure of existing files in the target folder
4. Update `CHANGELOG.md` under `[Unreleased]`
5. Open PR — include before/after use-case summary

### For a new course (high complexity)

1. Propose via issue first: what the course teaches, target audience, expected length
2. If approved, fork + branch: `courses/NN-your-course-name`
3. Structure per `courses/README.md`:
   ```
   courses/NN-name/
   ├── README.md
   ├── lessons/
   ├── exercises/
   ├── templates/
   └── examples/
   ```
4. Each lesson: markdown, <1000 words ideally, exercise at the end
5. Test with ≥3 real students before merging
6. Update `courses/README.md` planned table → mark as "Complete"
7. Update `CHANGELOG.md`, bump version

### For an example project

1. Build the project in a separate repo first — ship it, use it
2. Once proven, strip your production secrets + private data
3. Add comprehensive `.env.example` with fake values
4. Include BRD (`docs/BRD-*.md`), tests, QA scores
5. Copy into `examples/name/` as a PR
6. Must pass: `npm ci && npm run typecheck && npm run lint && npm run build`
7. Update `examples/README.md` planned table + `CHANGELOG.md`

### For install.sh / hooks / CLAUDE.md (high impact — core bootstrap)

1. Discuss via issue before writing code
2. Test end-to-end on a fresh macOS AND Linux VM — not just your machine
3. Version bump required (`v1.x.0` minor or `v2.0.0` breaking)
4. CHANGELOG under `[Unreleased]` describes every change
5. Mamoun reviews personally before merge

## Conventions

- **Commit messages:** conventional format (`feat:`, `fix:`, `docs:`, `chore:`, `refactor:`, `test:`)
- **Branch names:** `feat/short-description`, `fix/short-description`, `docs/short-description`
- **File naming:** `kebab-case.md` for docs, `SOP-Name.md` / `NAME-TEMPLATE.md` for structured content
- **Markdown:** ATX headers (`#`), no trailing punctuation in titles, 80-char lines where practical
- **No secrets anywhere:** even in example values. Use `xxx`, `your-key-here`, or similar
- **No MENA-specific content in English-only docs:** include Arabic version if user-facing
- **Arabic content:** Gulf conversational, not MSA

## Release process

Minor updates (bug fix, typo, small SOP addition):
- Merge to main
- No version tag
- CHANGELOG under `[Unreleased]`

Bigger updates (new course, new example, hook changes):
- Merge to main
- Bump version in CHANGELOG: move `[Unreleased]` items into a new `[X.Y.Z] — YYYY-MM-DD` section
- Tag: `git tag vX.Y.Z && git push origin vX.Y.Z`
- Publish GitHub Release with notes

## Don't contribute

- SMOrchestra internal SOPs (private — they live in `smorch-brain`)
- Production server runbooks
- Customer data / PII
- API keys (even rotated / fake-looking)
- Content requiring Tailscale or SMOrchestra server access to test
- Content that contradicts the core workflow in CLAUDE.md without a clear migration plan

## Questions

Open an issue at https://github.com/smorchestraai-code/eo-microsaas-training/issues
