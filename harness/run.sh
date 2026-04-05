#!/bin/bash
# ForgeProof Harness — Three-Agent Orchestration
#
# Usage:
#   ./harness/run.sh plan "Build the forgeproof-skill package with signing and verification"
#   ./harness/run.sh generate
#   ./harness/run.sh evaluate
#   ./harness/run.sh full "Brief description of what to build"
#
# The 'full' command runs all three agents in sequence.

set -euo pipefail

HARNESS_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$HARNESS_DIR")"

cd "$PROJECT_DIR"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log() { echo -e "${GREEN}[harness]${NC} $1"; }
warn() { echo -e "${YELLOW}[harness]${NC} $1"; }
err() { echo -e "${RED}[harness]${NC} $1"; }

run_planner() {
    local brief="$1"
    log "Starting Planner agent..."
    log "Brief: $brief"
    claude --model opus \
        "Read harness/planner.md. Then create a product spec for the following brief: $brief. Write the spec to spec.md in the project root."
    if [ -f spec.md ]; then
        log "Planner complete. Spec written to spec.md"
    else
        err "Planner did not produce spec.md"
        exit 1
    fi
}

run_generator() {
    if [ ! -f spec.md ]; then
        err "No spec.md found. Run the Planner first: ./harness/run.sh plan \"your brief\""
        exit 1
    fi
    log "Starting Generator agent..."
    claude --model opus \
        "Read harness/generator.md and spec.md. Implement the specification. Write a handoff artifact to harness/handoff.md after each major feature."
    log "Generator complete. Check harness/handoff.md for status."
}

run_evaluator() {
    if [ ! -f harness/handoff.md ] && [ ! -f spec.md ]; then
        err "No handoff.md or spec.md found. Run the Generator first."
        exit 1
    fi
    log "Starting Evaluator agent..."
    claude --model opus \
        "Read harness/evaluator.md, harness/criteria.md, and harness/handoff.md. Evaluate the ForgeProof skill implementation. Write your evaluation to harness/eval-report.md."
    if [ -f harness/eval-report.md ]; then
        log "Evaluator complete. Report at harness/eval-report.md"
        # Check for FAIL in the report
        if grep -q "Overall: FAIL" harness/eval-report.md 2>/dev/null; then
            warn "Evaluation FAILED. Review harness/eval-report.md for bugs."
        else
            log "Evaluation PASSED."
        fi
    else
        err "Evaluator did not produce eval-report.md"
        exit 1
    fi
}

run_fix() {
    if [ ! -f harness/eval-report.md ]; then
        err "No eval-report.md found. Run the Evaluator first."
        exit 1
    fi
    log "Starting Generator fix pass..."
    claude --model opus \
        "Read harness/generator.md, spec.md, and harness/eval-report.md. Fix all bugs listed in the evaluation report. Update harness/handoff.md when done."
    log "Fix pass complete. Re-run evaluator to verify: ./harness/run.sh evaluate"
}

case "${1:-help}" in
    plan)
        if [ -z "${2:-}" ]; then
            err "Usage: ./harness/run.sh plan \"your brief description\""
            exit 1
        fi
        run_planner "$2"
        ;;
    generate)
        run_generator
        ;;
    evaluate)
        run_evaluator
        ;;
    fix)
        run_fix
        ;;
    full)
        if [ -z "${2:-}" ]; then
            err "Usage: ./harness/run.sh full \"your brief description\""
            exit 1
        fi
        run_planner "$2"
        echo ""
        log "--- Planner done. Starting Generator in 3s... ---"
        sleep 3
        run_generator
        echo ""
        log "--- Generator done. Starting Evaluator in 3s... ---"
        sleep 3
        run_evaluator
        ;;
    help|*)
        echo "ForgeProof Harness — Three-Agent Orchestration"
        echo ""
        echo "Commands:"
        echo "  plan \"brief\"    Run the Planner to create spec.md"
        echo "  generate        Run the Generator to implement spec.md"
        echo "  evaluate        Run the Evaluator to test the implementation"
        echo "  fix             Run the Generator to fix bugs from eval-report.md"
        echo "  full \"brief\"    Run all three agents in sequence"
        echo ""
        echo "Typical flow:"
        echo "  1. ./harness/run.sh plan \"Build the forgeproof-skill package\""
        echo "  2. Review spec.md, edit if needed"
        echo "  3. ./harness/run.sh generate"
        echo "  4. ./harness/run.sh evaluate"
        echo "  5. If FAIL: ./harness/run.sh fix && ./harness/run.sh evaluate"
        ;;
esac
