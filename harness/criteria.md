# ForgeProof Harness — Grading Criteria

## Scoring

Each criterion is scored 1-10. The overall result is PASS if all criteria meet their threshold AND no Critical bugs exist.

---

## Criterion 1: Correctness (Weight: High, Threshold: 8/10)

**What it measures:** Does the code do what the spec says? Do tests pass? Does signing produce valid, verifiable bundles?

**Pass (8+):** All spec acceptance criteria met. Tests pass. Ed25519 sign/verify round-trip works. Decision log hash chain is valid. .rpack bundles pass verification.

**Fail (<8):** Any acceptance criterion not met. Tests fail. Crypto produces invalid signatures. Hash chain has gaps.

**Few-shot scoring:**
- 10/10: All features implemented, all tests pass, edge cases handled, crypto verified
- 8/10: All core features work, minor edge cases missing, tests pass
- 5/10: Core pipeline works but signing is broken or tests fail
- 3/10: Partial implementation, multiple features missing

---

## Criterion 2: Reliability (Weight: High, Threshold: 7/10)

**What it measures:** Does it handle errors gracefully? What happens with bad inputs, missing files, no network?

**Pass (7+):** Missing config falls back to defaults. Bad issue number gives clear error. Missing `gh` CLI detected in pre-flight. No unhandled exceptions on reasonable edge cases.

**Fail (<7):** Crashes on missing config. Cryptic errors on bad input. Unhandled exceptions in normal error paths.

**Few-shot scoring:**
- 10/10: Every error path tested, clear messages, graceful degradation
- 7/10: Common errors handled, rare edge cases may surface raw exceptions
- 4/10: Happy path works but errors cause crashes or confusing output
- 2/10: Fragile — breaks on slightly unexpected input

---

## Criterion 3: Integrity (Weight: High, Threshold: 9/10)

**What it measures:** Is the cryptographic provenance trustworthy? Can the .rpack be tampered with undetected? Is the hash chain continuous?

**Pass (9+):** Root digest binds MANIFEST + HASHES + POLICY. Signature covers the root digest. Modifying any artifact causes verification failure. Decision log hash chain has no gaps. Ephemeral keys are deleted after signing.

**Fail (<9):** Signature doesn't cover all artifacts. Hash chain can be broken without detection. Keys persist after signing. Verification passes on tampered bundles.

**Few-shot scoring:**
- 10/10: Full tamper-evidence, verified with adversarial test cases
- 9/10: All artifacts bound, verification rejects tampering, keys cleaned up
- 6/10: Signing works but verification is incomplete or hash chain has gaps
- 3/10: Signatures exist but don't actually protect against tampering

---

## Criterion 4: Usability (Weight: Medium, Threshold: 7/10)

**What it measures:** Can a developer install the skill and run `/forgeproof` without reading source code? Are error messages helpful?

**Pass (7+):** Install script works. Commands are discoverable. Output clearly shows progress through phases. Error messages tell the user what to do.

**Fail (<7):** Install requires manual steps not documented. Commands unclear. Output is confusing. Errors give no guidance.

**Few-shot scoring:**
- 10/10: Install is one command, commands self-document, errors include fix suggestions
- 7/10: Install works with README, commands work, errors are understandable
- 4/10: Requires reading source code to understand setup or usage
- 2/10: Doesn't install correctly or commands don't register

---

## Criterion 5: Code Quality (Weight: Medium, Threshold: 7/10)

**What it measures:** Is the code clean, typed, and following project conventions? Does ruff pass?

**Pass (7+):** Ruff clean. Type hints on all public functions. No dead code. Follows patterns from existing RPB library. Tests are meaningful (not just "assert True").

**Fail (<7):** Ruff errors. Missing type hints. Copy-pasted code with no adaptation. Tests are trivial or absent.

**Few-shot scoring:**
- 10/10: Production-quality, consistent style, comprehensive tests
- 7/10: Clean code, typed, ruff clean, reasonable test coverage
- 4/10: Works but messy — inconsistent style, some ruff errors, weak tests
- 2/10: Hacky, no types, no tests, linter errors throughout
