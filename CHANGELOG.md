# Changelog

All notable changes to ForgeProof are documented in this file.

## [1.0.1] - 2026-05-12

### Fixed
- **Plugin failed to load.** `hooks/hooks.json` was missing the top-level `"hooks"` wrapper expected by Claude Code's Zod schema, producing a validation error on install (reported via `/doctor`). The events are now nested under `hooks` and the file references `https://json.schemastore.org/claude-code-settings.json` for editor validation.
- **PreToolUse PR gate never fired.** The matcher `Bash(gh pr create)` is permission-rule syntax, not hook-matcher syntax (matchers are regex against the tool name only). The gate is now a regex match on `Bash`, with the command inspection handled by a new `gate-pr` subcommand in `forgeproof.py` that parses the hook event JSON from stdin and exits with code 2 (block + surface stderr to Claude) when no `.rpack` bundle is present.
- Hook command falls back from `python3` to `python` so the gate works on Linux installs that ship only `python3` and Windows installs that ship only `python`.

### Tests
- Added `TestCmdGatePr` covering allow/block paths, unrelated commands, non-Bash tools, and malformed stdin. 44 tests pass.

## [1.0.0] - 2026-04-15

Initial public release.

### Skills
- `/forgeproof <issue>` — Full 4-phase pipeline: parse & plan, generate, evaluate, package
- `/forgeproof-push` — Push branch and create PR with provenance metadata
- `/forgeproof-verify <path>` — Verify .rpack bundle integrity (signature, chain, artifacts)
- `/forgeproof-reset <issue|--all>` — Clean up provenance state, branches, and ephemeral keys

### Provenance Engine
- Ed25519-signed SHA-256 hash chain with tamper-evident block linkage
- Ephemeral keypair generation per bundle (private key deleted after signing)
- Multi-language toolchain detection (Python, TypeScript/JavaScript, Go)
- Explicit file staging (no `git add -A`) to prevent committing generated artifacts
- Re-run handling: `--force` flag on init, graceful branch/PR detection
- `reset` subcommand for cleaning up chains, bundles, and keys

### Hooks
- PreToolUse: blocks `gh pr create` without a signed .rpack bundle
- PostToolUse: runs project linter during active ForgeProof runs (scoped to sessions with an active chain)

### Testing
- 38 automated tests covering all subcommands, chain integrity, verification, and E2E pipeline
- `claude plugin validate` passes with 0 errors
- Validated end-to-end across 4 GitHub issues on a real Python project

### Security
- No external network calls beyond `gh` CLI and `ssh-keygen`
- No telemetry, analytics, or credential persistence
- All provenance data stored locally in `.forgeproof/`
