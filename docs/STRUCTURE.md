# Repository Structure

How this repo is organized and where to add new content.

## Layout

```
eo-microsaas-training/
├── README.md              # Entry point — what this repo is, one-command install
├── CLAUDE.md              # Student playbook → installed to ~/.claude/CLAUDE.md
├── settings.json          # Claude Code hooks → installed to ~/.claude/settings.json
├── install.sh             # One-command bootstrap (curl | bash)
├── CHANGELOG.md           # Version history
├── CONTRIBUTING.md        # How to add courses, examples, SOPs
├── LICENSE                # MIT
├── .gitignore
│
├── sops/                  # Standard Operating Procedures
│   ├── SOP-Quality-Scorecard.md      5-question PR scorecard
│   ├── SOP-Git-Workflow.md           Branches, commits, PRs
│   └── SOP-Deployment.md             Vercel / Netlify deploy
│
├── templates/             # Fill-in templates
│   ├── BRD-TEMPLATE.md               Write before coding
│   ├── QA-SCORECARD-TEMPLATE.md      Save to docs/qa-scores/ per PR
│   └── DEPLOY-CHECKLIST.md           Pre-flight every deploy
│
├── reference/             # Context docs (read, don't fill in)
│   └── DEVELOPMENT-WORKFLOW-EXPLAINED.md   The 7-step workflow
│
├── courses/               # Training courses (planned — see courses/README.md)
│   └── README.md
│
├── examples/              # Reference projects (planned — see examples/README.md)
│   └── README.md
│
└── docs/                  # Meta: how this repo works
    └── STRUCTURE.md       # You are here
```

## Root vs subfolders

- **Root-level files** are what `install.sh` deploys to a student's `~/.claude/` or other canonical locations. Moving them breaks the installer.
- **Subfolders** are content that stays in place (students read them from `~/eo-student-materials/` after install).

## Versioning

Every tagged release (`v1.0.0`, `v1.1.0`, etc.) is considered stable. Students can pin to a specific version via:

```bash
curl -sSL https://raw.githubusercontent.com/smorchestraai-code/eo-microsaas-training/v1.0.0/install.sh | bash
```

Main branch is always "latest stable."

## Adding content

| To add... | Create at | Commit message prefix |
|-----------|-----------|------------------------|
| A new SOP | `sops/SOP-NAME.md` | `sops:` |
| A new template | `templates/NAME-TEMPLATE.md` | `templates:` |
| A new reference doc | `reference/NAME.md` | `docs:` |
| A new course | `courses/NN-NAME/` | `courses:` |
| An example project | `examples/NAME/` | `examples:` |
| Update the playbook | `CLAUDE.md` | `feat:` or `docs:` |
| Update installer | `install.sh` | `feat:` or `fix:` |
| Update hooks | `settings.json` | `feat:` (security) or `fix:` |

Always:
- Update `CHANGELOG.md` with what changed
- Tag releases for major changes (`git tag v1.1.0 && git push origin v1.1.0`)
- Test the installer fully end-to-end on a fresh VM / container before tagging

## What doesn't belong here

- SMOrchestra internal SOPs (they live in `SMOrchestra-ai/smorch-brain`)
- Production server rebuild runbooks
- Customer data
- Anyone's API keys or credentials (even as examples)
- Anything requiring Tailscale / private server access

This repo is **public** and assumes students have zero SMOrchestra infrastructure access.
