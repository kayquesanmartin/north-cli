# 10 — Requirements & Software Engineering Process

The most expensive bugs are not coding errors — they are **building the wrong thing**. A defect in requirements that escapes to production can cost orders of magnitude more to fix than one caught during analysis. This file covers how to figure out *what* to build (requirements engineering) and *how* to organize the work of building it (process).

---

## 1. Requirements engineering

A discipline in its own right, with four core activities: **elicitation, analysis, specification, and validation** (plus ongoing management).

### Functional vs. Non-Functional Requirements (NFRs)
- **Functional requirements (FR)** describe *what* the system does — features and behaviors. Often captured as use cases or user stories; UML use-case diagrams are a common modeling tool ([arXiv — Elicitation and Modeling of NFRs](https://arxiv.org/pdf/1403.1936)).
- **Non-functional requirements (NFRs)** describe *how well* the system does it — the qualities/constraints. These are linked to functional requirements and are notoriously under-specified ([arXiv](https://arxiv.org/pdf/1403.1936)).

NFRs (the "-ilities") are where systems live or die at scale, and they're the ones developers most often forget to pin down:
- **Performance** (latency, throughput) · **Scalability** · **Availability** (the number of 9s) · **Reliability** · **Security** · **Maintainability** · **Observability** · **Usability** · **Compliance** (GDPR, LGPD, PCI).

> **Senior practice:** make NFRs *measurable*. "Fast" is not a requirement; "p99 latency < 200ms at 5k RPS" is. "Highly available" is not a requirement; "99.95% monthly availability" is — and that number directly dictates your architecture (single-region vs multi-region, [file 09](09-distributed-data.md)). The reason NFRs get neglected is that they're hard to elicit and easy to leave vague ([arXiv](https://arxiv.org/pdf/1403.1936)).

### Elicitation techniques
Interviews, workshops, observation, prototyping, document analysis, and questionnaires. A practical technique from the NFR literature: attach targeted questions to each functional requirement to surface the NFRs hiding behind it — e.g., for a "user logs in" FR, ask about acceptable response time, concurrent users, and lockout/security rules ([arXiv](https://arxiv.org/pdf/1403.1936)).

### Quality of a good requirement
Each requirement should be: **unambiguous, testable/verifiable, complete, consistent, traceable, and feasible.** If you can't write a test that proves a requirement is met, it isn't a requirement yet — it's a wish.

---

## 2. The SDLC and its process models

The Software Development Life Cycle phases — requirements, design, implementation, testing, deployment, maintenance — are constant. What differs is how you *sequence and iterate* them.

- **Waterfall** — sequential phases, each completed before the next. Works only when requirements are genuinely fixed and well understood (rare in software). Its failure mode: you discover the requirements were wrong after building everything.
- **Iterative & Incremental** — build in repeated cycles, each producing working software. The foundation of all modern approaches.
- **Agile** — the umbrella for iterative methods emphasizing the [Agile Manifesto](https://agilemanifesto.org/) values: individuals and interactions, working software, customer collaboration, and responding to change. Agile is a *mindset*, not a ceremony set.
  - **Scrum** — fixed-length sprints, defined roles (Product Owner, Scrum Master, Dev Team), and ceremonies (planning, daily standup, review, retrospective). Good for feature delivery with evolving priorities.
  - **Kanban** — continuous flow, visualize work, limit work-in-progress (WIP), optimize cycle time. Good for support/ops and steady streams of work.
- **XP (Extreme Programming)** — the engineering-practice-heavy method that gave us TDD, pair programming, continuous integration, and small releases. The practices outlived the brand.

**Senior caution:** most "Agile" failures are cargo-cult Agile — running the ceremonies while ignoring the values (working software, fast feedback, technical excellence). Process is a means; shipping valuable, changeable software is the end.

---

## 3. Estimation — and why it's hard

- **Relative estimation** (story points, planning poker) sidesteps the false precision of hour estimates by comparing items to each other.
- **#NoEstimates** and forecasting via historical throughput (how many items the team *actually* finishes per week) is often more accurate than upfront estimates.
- **Cone of uncertainty** — early estimates can be off by 4x in either direction; precision improves only as you learn. Communicate ranges, not points.
- Beware **Hofstadter's Law**: "It always takes longer than you expect, even when you take into account Hofstadter's Law."

---

## 4. Engineering practices that make process work

Process is hollow without the technical practices that enable fast, safe iteration:
- **Version control discipline** — small, frequent commits; trunk-based development or short-lived branches; meaningful messages.
- **CI/CD** — every commit is built and tested automatically; deployable artifacts are produced continuously and released frequently and safely (feature flags, canary, blue-green).
- **Code review** — the highest-ROI quality practice; catches defects *and* spreads knowledge. Keep PRs small.
- **Definition of Done** — shared, explicit criteria (tested, reviewed, documented, deployed) so "done" isn't ambiguous.
- **Technical debt management** — debt is a real, sometimes-rational tool (ship now, pay interest later), but untracked debt compounds until the system ossifies. Make it visible and pay it deliberately.

> The DORA research (*Accelerate*, [file 13](13-reading-list.md)) empirically links four metrics — deployment frequency, lead time for changes, change failure rate, and mean time to recovery — to organizational performance. They're the best available scoreboard for whether your process actually works.

---

## Key sources
- [Elicitation and Modeling Non-Functional Requirements — arXiv](https://arxiv.org/pdf/1403.1936) · [Eliciting & documenting NFRs — r/SoftwareEngineering](https://www.reddit.com/r/SoftwareEngineering/comments/1h7zx30/eliciting_understanding_and_documenting/).
- Karl Wiegers — *Software Requirements*; the [Agile Manifesto](https://agilemanifesto.org/).
- Forsgren, Humble, Kim — *Accelerate* (DORA metrics); see [file 13](13-reading-list.md).
