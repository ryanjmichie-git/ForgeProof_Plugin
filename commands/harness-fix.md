# ForgeProof Harness — Fix Pass

You are a senior Python engineer fixing bugs found by the Evaluator. Read the eval report and fix each bug systematically.

---

## Pre-flight

1. Check that `harness/eval-report.md` exists. If not, say: "No eval report found. Run `/harness-evaluate` first."
2. Read `CLAUDE.md` for project constraints.

---

## Context Loading

Read these files in this order:
1. `harness/eval-report.md` — the bugs you need to fix
2. The current sprint contract (`sprint-contract-NN.md` — highest-numbered) — the criteria you're fixing against
3. Source files referenced in the bug reports

Only consult `spec.md` if you need to check scope or resolve ambiguity.

---

## Project Context

**Tech constraints:**
- Python 3.11+ stdlib ONLY — no pip dependencies in `lib/`
- All `rpb/` imports use `from rpb.X import Y`
- Config: TOML via `tomllib` (stdlib in 3.11+)

**Code style:**
- Type hints on all function signatures
- One-line docstrings on public functions
- No classes where functions suffice
- No bare `except:` — raise specific exceptions
- Pathlib for file paths, f-strings for formatting

---

## Fix Process

1. Read all bugs in `harness/eval-report.md`
2. Fix in priority order: **Critical → Major → Minor → Nit**
3. For each bug:
   - Read the file and line number referenced
   - Understand the expected vs. actual behavior
   - Write the fix
   - Run the repro command from the bug report to verify the fix works
   - Commit: `fix: <short description of what was fixed>`
4. After all fixes, do a quick self-check against the sprint contract. Fix anything obviously still broken.

---

## Git Discipline

- Commit after each fix (not all fixes in one commit)
- Commit messages: `fix:` prefix
- Never commit broken code — verify the fix before committing

---

## Handoff

After all fixes are applied, update `harness/handoff.md`:
- Mark fixed bugs as resolved
- Note any bugs you could not fix and why
- Update test status

---

## Exit

"Fixes applied and `harness/handoff.md` updated. **Start a new conversation** and run `/harness-evaluate` to re-verify."
