# 14 — Spec-Driven Development (SDD) & AI-Assisted Engineering

The rise of capable AI coding agents has inverted an old trade-off. For decades, heavy upfront specification was a *cost* you paid to coordinate humans; agile reduced it because writing detailed specs that humans then ignored was waste. With AI agents, a precise specification becomes the **highest-leverage artifact you can produce** — because the agent will faithfully build whatever you specify, including your ambiguities and mistakes. SDD is the methodology that puts that specification back at the center.

> **Spec-Driven Development (SDD)** is a methodology that puts specifications at the center of AI-assisted software development. Instead of jumping straight to code, you describe *what* to build, refine it through structured phases, and let your AI coding agent implement it ([GitHub Spec Kit docs](https://github.github.com/spec-kit/)).

The shift Kiro names explicitly: from *vibe coding* (prompt → code → hope) to "a real, durable collaboration between the programmer and the AI development agent," because the intent is captured in **version-controlled artifacts** the human can read, review, and edit ([Kiro — the future of AI spec-driven development](https://kiro.dev/blog/kiro-and-the-future-of-software-development/)).

---

## 1. The core SDD loop: Spec → Plan → Tasks → Implement

GitHub's Spec Kit ships this exact four-phase process; each phase produces a **Markdown artifact that feeds the next**, giving the agent structured context instead of ad-hoc prompts ([Spec Kit docs](https://github.github.com/spec-kit/)).

| Phase | Spec Kit command | Produces | The discipline |
|---|---|---|---|
| **0. Principles** | `/speckit.constitution` | project principles ("constitution") | Establish non-negotiables (language, style, testing policy) once |
| **1. Specify** | `/speckit.specify` | the spec (what & why) | Be explicit about *what* and *why*; **do NOT mention the tech stack yet** ([Spec Kit](https://github.com/github/spec-kit)) |
| **2. Plan** | `/speckit.plan` | technical plan | *Now* specify tech stack, architecture, constraints ([Spec Kit](https://github.com/github/spec-kit)) |
| **3. Tasks** | `/speckit.tasks` | `tasks.md` | Break the plan into discrete, dependency-ordered, individually-verifiable tasks |
| **4. Implement** | `/speckit.implement` | code | Agent executes tasks systematically, respecting dependencies |

Why separating *what* from *how* matters: forcing the spec phase to ignore the tech stack keeps it about user value and behavior, which makes it reviewable by non-engineers and reusable across implementations. Spec Kit even uses this for **creative exploration** — generating parallel implementations across different stacks from one spec ([Spec Kit](https://github.com/github/spec-kit)).

Spec Kit's task breakdown is notable for being **organized by user story**, with dependency management (models before services, services before endpoints), an optional **TDD structure** (test tasks ordered before implementation), and **checkpoint validation** per story so each is independently functional ([Spec Kit](https://github.com/github/spec-kit)).

---

## 2. Kiro's three-file spec model

AWS's Kiro formalizes a spec as **three Markdown files** that transform an idea into executable work ([Kiro — Specs docs](https://kiro.dev/docs/specs/)):

1. **`requirements.md`** — user stories and acceptance criteria in structured notation (for bugs, a `bugfix.md` capturing current vs. expected vs. unchanged behavior).
2. **`design.md`** — technical architecture, **sequence diagrams**, data flow, error handling, and testing strategy.
3. **`tasks.md`** — discrete, trackable implementation tasks with real-time status, runnable individually or all at once.

Kiro offers two workflow variants — **Requirements-First** or **Design-First** — and, when running all tasks, analyzes dependencies to run independent ones concurrently ([Kiro docs](https://kiro.dev/docs/specs/)). The value, in Kiro's framing: working at the spec level lets you "zoom out" above implementation detail to understand purpose, make structural changes, and communicate intent — and because specs are version-controlled, a requirement change is a two-line edit to `requirements.md` that the agent then propagates into tasks and code ([Kiro blog](https://kiro.dev/blog/kiro-and-the-future-of-software-development/)).

> **Greenfield vs. brownfield:** SDD applies to both — generating from scratch ("0-to-1"), and iterative enhancement / legacy modernization where you add features and adapt processes incrementally ([Spec Kit](https://github.com/github/spec-kit)).

---

## 3. Agent context files: `AGENTS.md` / `CLAUDE.md`

Distinct from a *per-feature* spec, this is the **persistent, repo-level operating manual for the agent**. `AGENTS.md` is a Markdown file at the repo root that gives AI coding agents project-specific operational guidance the agent **cannot infer from the code alone**: build/test commands, coding conventions, architectural constraints, and "do nots" ([Augment Code — How to build AGENTS.md](https://www.augmentcode.com/guides/how-to-build-agents-md); [agents.md](https://agents.md)).

What belongs in it:
- How to **build, run, and test** (exact commands).
- **Conventions** the agent should follow (naming, structure, error handling, the patterns from [files 05–06](05-clean-code-solid.md)).
- **Constraints & guardrails** (don't touch `legacy/`, never commit secrets, always run the linter).
- **Architecture orientation** (where things live, the module boundaries from [file 01](01-architecture-principles.md)).

> **Caveat (stay empirical):** a bigger context file is not automatically better. Some research has found that poorly-written or bloated `AGENTS.md` files can *reduce* agent success rates ([r/ClaudeAI discussion](https://www.reddit.com/r/ClaudeAI/comments/1r7mvja/new_research_agentsmd_files_reduce_coding_agent/)). Keep it concise, accurate, and current — treat it like code: review it, and delete stale guidance.

---

## 4. How SDD relates to the classic documents

SDD didn't invent specification — it operationalized it for agents. The mapping:
- The SDD **spec/`requirements.md`** is a lightweight, agent-targeted [PRD + requirements doc](15-engineering-documents.md).
- The SDD **`design.md`/plan** is a lightweight [technical design doc / RFC](15-engineering-documents.md), often with [C4 or UML diagrams](16-diagramming.md).
- SDD **`tasks.md`** is sprint/backlog decomposition (file 15) made machine-executable.
- The **constitution** and **`AGENTS.md`** encode standing [architecture decisions (ADRs)](15-engineering-documents.md) and conventions.

The reason to keep the classic forms in mind: they tell you *what makes each section good* (e.g., a design doc's value is its trade-offs and alternatives — see [file 15](15-engineering-documents.md)). SDD gives you the workflow; the classic doc discipline gives you the quality bar.

---

## 5. Practical playbook for AI-assisted delivery

1. **Establish a constitution / `AGENTS.md` first.** Encode standards once so every task inherits them.
2. **Write the spec before code**, and keep it free of premature tech choices.
3. **Review the spec and the task plan like you'd review a PR** — this is where you catch wrong assumptions cheaply, before any code exists.
4. **Keep specs in version control** alongside the code they describe; a changed requirement should be a diff.
5. **Decompose into small, verifiable tasks** with explicit dependencies and, where possible, tests-first.
6. **Treat the agent's output as a junior engineer's PR** — read it, test it, and hold it to the [clean code](05-clean-code-solid.md), [testing](07-testing-tdd.md), and [security](18-cybersecurity.md) bars. SDD makes the agent faster; it does not remove your accountability for correctness.
7. **Update the spec when reality diverges** — a spec that lies is worse than no spec.

---

## Key sources
- [GitHub Spec Kit — repo](https://github.com/github/spec-kit) and [documentation](https://github.github.com/spec-kit/).
- [Kiro — Specs documentation](https://kiro.dev/docs/specs/) and [Kiro and the future of AI spec-driven software development](https://kiro.dev/blog/kiro-and-the-future-of-software-development/).
- [agents.md](https://agents.md) and [How to Build Your AGENTS.md — Augment Code](https://www.augmentcode.com/guides/how-to-build-agents-md).
