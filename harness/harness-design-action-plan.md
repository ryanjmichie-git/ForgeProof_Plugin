# Harness Design for Long-Running Application Development

## Action Plan Based on Anthropic Engineering Blog (March 2026)

Source: [Anthropic Engineering - Harness Design for Long-Running Apps](https://www.anthropic.com/engineering/harness-design-long-running-apps)

---

## What This Is

Anthropic published their internal methodology for getting Claude to autonomously build complete applications over multi-hour sessions. The core insight: **harness design is the key lever for frontier agentic performance**, not just model capability.

A "harness" is the scaffolding around the model — the agent architecture, prompting strategy, evaluation loops, and context management that turn a raw LLM into something that can sustain coherent, high-quality work over hours.

---

## The Three-Agent Architecture

Anthropic's production harness uses three specialized agents. Each encodes a separation of concerns that solves a specific failure mode:

### Agent 1: Planner

**What it does:** Converts your brief prompt (1-4 sentences) into a comprehensive product specification.

**Why it exists:** Without a spec, the generator drifts, makes inconsistent decisions, and produces incoherent output over long sessions.

**Key behaviors to configure:**
- Focus on deliverables and high-level technical strategy, NOT granular implementation steps
- Proactively identify AI-powered features that could be woven into the app
- Produce ambitious scope while remaining implementable
- Output a structured spec document (markdown file) that the Generator reads

**Your action:** Create a `planner.md` prompt file that instructs the Planner agent on:
- Your preferred tech stack (React/Vite + FastAPI + SQLite is Anthropic's tested default)
- Your quality bar and design philosophy
- What "done" looks like for your projects
- How to structure the spec output (sections, format, level of detail)

### Agent 2: Generator

**What it does:** Implements the spec, feature by feature, with git version control throughout.

**Why it exists:** This is the builder. The key insight is that it should NOT self-evaluate its own work (see below).

**Key behaviors to configure:**
- Read the Planner's spec file at start
- Implement incrementally (sprint-based for Sonnet; continuous for Opus)
- Maintain git history so work can be rolled back
- Write structured handoff artifacts when passing to Evaluator
- For AI-integrated features: build proper agents that drive app functionality through tools (this required substantial prompt tuning because training data for this pattern is thin)

**Your action:** Create a `generator.md` prompt file that includes:
- Your tech stack constraints and preferences
- Code style and architecture patterns you want followed
- Instructions for git commit discipline
- How to handle edge cases and error states
- What to write into the handoff artifact for the Evaluator

### Agent 3: Evaluator

**What it does:** Tests the running application using Playwright MCP, grades it against hard criteria, and files specific actionable bugs.

**Why it exists:** Self-evaluation is broken. When asked to evaluate their own work, agents confidently praise it even when quality is obviously mediocre. A separate evaluator agent, tuned toward skepticism, solves this.

**Key behaviors to configure:**
- Use Playwright MCP to actually interact with the live application (click, type, navigate)
- Test UI features, API endpoints, and database states directly
- Grade against explicit thresholds across defined criteria
- File specific, actionable bug reports (not vague feedback)
- Establish "sprint contracts" with the Generator before implementation begins

**Your action:** Create an `evaluator.md` prompt file that defines:
- Your grading criteria and their weights
- Hard pass/fail thresholds
- Instructions to be skeptical by default (counteract praise bias)
- How to write actionable bug reports
- What tools it has access to (Playwright, curl, database queries, etc.)

---

## The Four Grading Criteria (Adapt These to Your Domain)

Anthropic's evaluation framework for frontend design:

| Criterion | What It Measures | Weight |
|-----------|-----------------|--------|
| **Design Quality** | Coherence, mood, distinct identity through color/typography/layout | High |
| **Originality** | Custom decisions; penalizes template layouts, library defaults, generic AI patterns | High |
| **Craft** | Typography hierarchy, spacing consistency, color harmony, contrast ratios | Medium |
| **Functionality** | Usability independent of aesthetics; can a user complete tasks? | Medium |

**Key insight:** Weight criteria where the model is weakest (quality, originality) heavier than where it's already adequate (craft, functionality). This drives the most improvement.

**Your action:** Define 3-5 grading criteria for your own projects. For each:
- Write a 1-sentence definition
- Define what a "pass" looks like vs. a "fail"
- Assign relative weight
- Include 1-2 few-shot examples showing how to score

---

## Sprint Contracts (The Secret Weapon)

Before the Generator starts building a feature, the Generator and Evaluator negotiate a "sprint contract" — an explicit agreement on what will be built and exactly how success will be verified.

**Example:** A level editor sprint contained 27 discrete test criteria before a single line of code was written.

**Why this works:** It eliminates the ambiguity that causes agents to ship half-baked features and evaluators to wave through incomplete work.

**Your action:**
1. Before each major feature, have the Generator propose: "Here's what I'll build and here's how you can verify each piece"
2. Have the Evaluator review and push back: "You're missing edge case X" or "How will I test Y?"
3. Both iterate until agreed
4. Generator implements against the contract
5. Evaluator tests against the explicit criteria

---

## Context Management (The Hardest Part)

### The Problem

Long sessions cause two failures:
1. **Context degradation** — the model loses coherence as context fills up
2. **Context anxiety** — the model prematurely wraps up work because it senses the context limit approaching

### Two Solutions (Choose Based on Model)

**For Sonnet-class models:** Use context resets with structured handoff artifacts
- Clear the context window entirely between agents/sprints
- Pass a file containing: project state, what's been done, what's next, key decisions made
- Provides a "clean slate" that eliminates anxiety
- Requires comprehensive handoff artifacts (the handoff file IS the continuity)

**For Opus-class models:** Use automatic compaction (Claude Agent SDK handles this)
- The model can sustain coherent work across 2+ hours without manual resets
- SDK-level compaction summarizes conversation in-place as needed
- Simpler to implement but retains some context anxiety

### File-Based Communication Between Agents

Critical pattern: agents communicate via files, NOT inline conversation.
- Previous agent writes a structured file (spec, handoff, bug report)
- Next agent reads that file as its starting context
- This prevents context pollution and enables clean transitions

**Your action:**
1. Create a `handoff-template.md` that defines what information must be passed between agents:
   - Current project state
   - Completed features (with test status)
   - Remaining work
   - Key architectural decisions and why
   - Known issues / technical debt
   - Git branch state
2. For Sonnet: implement explicit context resets between sprints
3. For Opus: rely on SDK compaction but keep handoff files as a safety net

---

## Implementation Steps (In Order)

### Phase 1: Set Up the Infrastructure (Day 1)

1. **Install prerequisites:**
   ```bash
   # Claude Code (if not already installed)
   # Playwright MCP server for the Evaluator
   npm install -g @anthropic-ai/claude-code
   npm install -g playwright
   npx playwright install
   ```

2. **Create your project harness directory:**
   ```
   harness/
     planner.md          # Planner agent prompt
     generator.md        # Generator agent prompt
     evaluator.md        # Evaluator agent prompt
     handoff-template.md # Structured handoff format
     criteria.md         # Your grading criteria + few-shot examples
     run.sh              # Script to orchestrate the three agents
   ```

3. **Set up the default tech stack** (Anthropic's tested stack):
   - Frontend: React + Vite
   - Backend: FastAPI (Python) or Express (Node)
   - Database: SQLite for development, PostgreSQL for production
   - Testing: Playwright for E2E
   - Version control: git (commit after each sprint)

### Phase 2: Write Your Agent Prompts (Day 2-3)

4. **Write `planner.md`** — start simple:
   - "You are a product architect. Given a brief description, produce a comprehensive product specification..."
   - Include your preferred tech stack
   - Include examples of good specs you've written or seen
   - Instruct it to identify AI-powered features

5. **Write `generator.md`** — the longest prompt:
   - "You are a senior full-stack engineer. Read the spec file at [path] and implement it..."
   - Include your code style preferences
   - Include architecture patterns (component structure, API design, etc.)
   - Instruct git discipline: commit after each feature, meaningful messages
   - Include handoff artifact instructions

6. **Write `evaluator.md`** — the most important prompt:
   - "You are a skeptical QA engineer. Your job is to find problems, not praise."
   - Include your grading criteria with few-shot score examples
   - Instruct Playwright usage for live testing
   - Define the bug report format
   - Set hard thresholds: "If Design Quality < 7/10, fail the sprint"

### Phase 3: Run Your First Build (Day 4)

7. **Start small:** Pick a simple but complete app (a task manager, a notes app, a dashboard)

8. **Run the Planner:**
   ```bash
   claude --model opus "Read planner.md and create a product spec for: [your 2-sentence app idea]. Write the spec to spec.md"
   ```

9. **Run the Generator:**
   ```bash
   claude --model opus "Read generator.md and spec.md. Implement this application. Write a handoff artifact to handoff.md when each major feature is complete."
   ```

10. **Run the Evaluator:**
    ```bash
    claude --model opus "Read evaluator.md, criteria.md, and handoff.md. The application is running at localhost:5173. Use Playwright to test it. Write your evaluation to eval-report.md."
    ```

11. **Iterate:** If the Evaluator files bugs, send the Generator back with the eval report

### Phase 4: Tune and Simplify (Week 2+)

12. **Read evaluator logs:** Find where the Evaluator's judgment diverges from yours. Update `evaluator.md` to address those gaps

13. **Stress-test assumptions:** Every component in your harness encodes an assumption about what the model can't do alone. Test each one:
    - Remove sprint decomposition. Does quality hold?
    - Remove the Evaluator for simple tasks. Does quality hold?
    - Let the Generator self-evaluate. Does it catch real issues?

14. **Simplify when possible:** Per Anthropic's key principle: "As models improve, the harness should get simpler, not more complex." When Opus 4.6 shipped, they removed sprint decomposition entirely — the model could sustain coherent 2-hour builds without it.

---

## Cost and Time Reference

From Anthropic's published results:

| Approach | Duration | Cost | Quality |
|----------|----------|------|---------|
| Single-agent baseline | 20 min | ~$9 | Non-functional core features |
| Full three-agent harness | 6 hours | ~$200 | Fully playable application |
| Simplified harness (Opus 4.6) | 3 hr 50 min | ~$125 | Working DAW with AI features |

The Planner is cheap (~$0.50, ~5 min). The Generator is where cost lives. The Evaluator adds modest cost but massive quality improvement on complex tasks.

---

## Key Lessons from Anthropic

1. **Self-evaluation is broken.** Never rely on the same agent to evaluate its own work. Use a separate evaluator, tuned toward skepticism.

2. **Prompt wording shapes output character.** Phrases like "the best designs are museum quality" created visual convergence effects. Be intentional about the aesthetic and quality language in your prompts.

3. **Iteration enables emergence.** By iteration 9 of a museum website, they had a competent dark-themed design. Iteration 10 produced a radical CSS 3D perspective room with doorway navigation. This emergent creativity only appears across many cycles.

4. **Every harness component encodes an assumption.** Those assumptions go stale as models improve. Stress-test regularly. Remove what's no longer load-bearing.

5. **Sprint contracts prevent ambiguity.** The Evaluator and Generator agreeing on explicit success criteria BEFORE implementation eliminates the most common failure mode.

6. **AI feature integration requires extra prompt work.** Getting the Generator to build proper agent-driven features (not just static apps) required substantial tuning because this pattern has thin training data coverage.

---

## What to Build First

Start with these progressively harder projects to calibrate your harness:

1. **Simple CRUD app** (task manager) — tests basic Generator + Evaluator loop
2. **Dashboard with real data** (API integration) — tests Planner spec quality + data handling
3. **AI-integrated tool** (e.g., a research assistant with tool use) — tests the full stack including agent features
4. **Multi-feature SaaS** (auth, dashboard, settings, payments) — tests long-running coherence and sprint contracts

Each build will reveal what to tune in your prompts. That's the point. The harness improves through use.
