# ForgeProof Skill

## What This Is

A Claude Code skill (`/forgeproof`) that converts GitHub issues into working code with cryptographically signed provenance bundles (.rpack). Claude Code itself is the reasoning engine — no Anthropic API keys needed.

## Architecture

- `commands/*.md` — Claude Code custom commands (slash commands)
- `lib/provenance.py` — CLI: builds + signs .rpack bundles
- `lib/decision_log.py` — CLI: appends hash-chained audit log entries
- `lib/config.py` — loads `.forgeproof.toml` with defaults (stdlib `tomllib`)
- `lib/rpb/` — pure-Python crypto library (Ed25519, SHA-256, .rpack packing/verification)
- `install.sh` — copies commands + lib into target project
- `templates/pr_body.md` — PR description template

## Tech Constraints

- **Python 3.11+ stdlib ONLY** — no pip dependencies anywhere
- All `rpb/` imports use `from rpb.X import Y` (lib/ is added to sys.path at runtime)
- Config uses TOML (`tomllib` — stdlib in 3.11+)
- External tools assumed: `gh` CLI, `git`, `python3`

## Commands

- `/forgeproof <issue-number>` — full 4-phase pipeline (parse, generate, evaluate, package)
- `/forgeproof-push` — create branch + PR from local changes
- `/forgeproof-verify <path>` — verify .rpack bundle integrity

## Status

- v1 complete: 26 tests passing, ruff clean, E2E verified
- Ed25519 signing works, integrity claims verified
- Tests are in the parent repo (`c:\Dev\ForgeProof\tests\test_skill_*.py`)

## What's Next

- v2: Add MCP server layer for Claude Desktop/Cursor support
- Multi-language support (currently Python-focused)
- Plugin marketplace publishing
- Move tests into this repo

## Harness (Three-Agent Architecture)

Located in `harness/` — based on Anthropic's engineering blog for long-running app development.

- `harness-design-action-plan.md` — source methodology and instructions to follow
- `planner.md` — converts brief → spec
- `generator.md` — implements spec with git discipline
- `evaluator.md` — skeptical QA, grades against criteria
- `criteria.md` — 5 grading criteria with pass/fail thresholds
- `handoff-template.md` — structured Generator → Evaluator handoff format
- `run.sh` — orchestration script

**Slash commands (primary — use these in VS Code):**

- `/harness-plan <brief>` — Planner: converts brief into spec.md
- `/harness-generate` — Generator: implements spec.md, writes sprint-contract-NN.md + harness/handoff.md
- `/harness-evaluate` — Evaluator: tests against current sprint contract + criteria, writes harness/eval-report.md
- `/harness-fix` — Generator fix pass: addresses bugs from eval-report.md

**Workflow:** Plan → review spec → Generate (with sprint contracts) → Evaluate → Fix (if needed) → re-Evaluate
**Key rule:** Start a new conversation between phases for clean context.

**Shell alternative (reference):** `./harness/run.sh full "your brief description"`

## Related Repos

- **Parent project:** `c:\Dev\ForgeProof` → github.com/ryanjmichie-git/ForgeProof
- **This repo:** `c:\Dev\FORGEPROOF_SKILL2` → github.com/ryanjmichie-git/FORGEPROOF_SKILL2
- **Design spec:** `c:\Dev\ForgeProof\docs\superpowers\specs\2026-03-31-forgeproof-skill-design.md`
- **Implementation plan:** `c:\Dev\ForgeProof\docs\superpowers\plans\2026-03-31-forgeproof-skill.md`
