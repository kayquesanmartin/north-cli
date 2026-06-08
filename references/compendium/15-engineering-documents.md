# 15 — Engineering Documents: PRD, RFC/Design Doc, ADR, FSD/SDD, SRS

Every document below answers a different question and lives at a different altitude. Confusing them is the most common documentation failure: a PRD that dictates implementation, or a design doc that re-litigates *what* to build. The senior skill is knowing which document a situation needs — and writing the *least* documentation that still de-risks the decision. The whole catalog also feeds directly into [Spec-Driven Development](14-spec-driven-development.md): each classic doc becomes a structured input for an AI agent.

| Document | Altitude | Owner | Answers |
|---|---|---|---|
| **PRD** | Product | Product Manager | *What* should we build and *why* (for users/business)? |
| **SRS / Requirements** | Requirements | BA / PM / Eng | *What exactly* must the system do (functional + non-functional)? |
| **FSD / FDD** | Functional design | BA / Eng | *How* will the system behave to satisfy requirements (observable behavior)? |
| **RFC / Design Doc / SDD** | Technical design | Engineer | *How* will we build it technically, and what did we trade off? |
| **ADR** | Decision | Engineer | *Why* did we choose this option over alternatives? |

---

## 1. PRD — Product Requirements Document

The PRD defines the product/feature from the *user and business* perspective. It should focus on **goals, not implementation** — explicitly *not* button placement or UI behavior, which is design's job ([r/ProductManagement — PRD guidance](https://www.reddit.com/r/ProductManagement/comments/r5q2iq/does_anyone_have_example_prds/)).

A widely-used structure ([Atlassian — What is a PRD](https://www.atlassian.com/agile/product-management/requirements)):
1. **Project specifics** — participants (owner, team, stakeholders), status, target release.
2. **Team goals & business objectives** — concise; inform, don't bore.
3. **Background & strategic fit** — the motivation and how it aligns with company goals.
4. **Assumptions** — about technology, business, and user behavior.
5. **User stories** — with links to interviews and **success metrics**.
6. **User interaction & design** — links to wireframes/explorations (not prescriptions).
7. **Questions** — a table of "things we need to decide or research."
8. **What we're NOT doing** — explicit out-of-scope to keep the team focused ([Atlassian](https://www.atlassian.com/agile/product-management/requirements)).

Hard-won practices: separate **decisions from explanations** (decisions in the first few pages, detail in an appendix); give a **prioritized** requirement list labeled **P0 (essential) / P1 (value-driving) / P2 (nice-to-have)**; include a short **non-requirements** list; and if a requirement contains "and," split it into two ([r/ProductManagement](https://www.reddit.com/r/ProductManagement/comments/r5q2iq/does_anyone_have_example_prds/)). The best PRDs are concise, scope-focused, skimmable, and pose open questions for collaborative decisions ([r/ProductManagement](https://www.reddit.com/r/ProductManagement/comments/r5q2iq/does_anyone_have_example_prds/)).

---

## 2. SRS / Requirements specification

The bridge from product intent to engineering precision (see [file 10](10-requirements-process.md) for the discipline). It captures **functional requirements** (what the system does) and **non-functional requirements** (the "-ilities": performance, security, availability, etc.), each **traceable** back to a business need and forward to test cases. The IEEE 830 / ISO 29148 lineage gives the formal structure; in agile shops this is often distributed across user stories with acceptance criteria rather than one monolith. The quality bar is unchanged: every requirement **unambiguous, testable, complete, consistent, traceable**.

---

## 3. FSD / FDD — Functional (Specification/Design) Document

The FSD describes **how the system will *behave*** to satisfy requirements — the observable inputs, outputs, and process flows — *without* prescribing the internal technical implementation. It is built from the high-level business requirements and provides **traceability** back to them ([Stanford — Functional Specification Document template](https://uit.stanford.edu/sites/default/files/2017/08/30/Functional%20Specification%20Document%20Template.docx)).

Typical contents ([Stanford template](https://uit.stanford.edu/sites/default/files/2017/08/30/Functional%20Specification%20Document%20Template.docx); [Imperium Dynamics — How to write an FDD](https://imperiumdynamics.com/blog/How-to-Write-a-Functional-Design-Document.html)):
- **Project scope**, business need/problem, background.
- **Risks & assumptions** (including third-party components, environment constraints).
- **Product overview.**
- **Context / data-flow / process-flow diagrams**, screen flows, sitemaps, mockups.
- **Use cases** — typical user interactions.
- **Functional requirements** — features, inputs, outputs, expected behaviors, grouped by screen/role/area.
- **Error reporting** — how errors/exceptions are handled.
- **Non-functional requirements** — performance, security, usability.
- **Integration/interface needs** — external hardware/software/users, APIs, schemas, error conditions.

Written in **non-technical language** so all stakeholders can read it, and typically **approved by both business and IT sponsors** before technical design begins ([Imperium Dynamics](https://imperiumdynamics.com/blog/How-to-Write-a-Functional-Design-Document.html)). Microsoft documents a combined **FDD/TDD** that adds technical design and a dedicated **security requirements** section per custom role ([Microsoft Learn — FDD/TDD](https://learn.microsoft.com/en-us/dynamics365/guidance/patterns/create-functional-technical-design-document)).

> **Note on "SDD":** the acronym is overloaded. It can mean **Software Design Document** (the technical design, ≈ the RFC below), **System Design Document**, or — in the AI era — **Spec-Driven Development** ([file 14](14-spec-driven-development.md)). Always clarify which your team means.

---

## 4. RFC / Design Doc — Technical design

The engineer's document. Written *before* coding to capture the **high-level implementation strategy and key design decisions, with emphasis on the trade-offs considered** ([Industrial Empathy — Design Docs at Google](https://www.industrialempathy.com/posts/design-docs-at-google/)). RFCs ("Request for Comment," also called Design Docs) build software faster by clarifying assumptions and circulating plans early, for non-trivial projects and cross-team decisions ([Pragmatic Engineer — RFC and Design Doc examples](https://newsletter.pragmaticengineer.com/p/software-engineering-rfc-and-design)).

**Google's canonical structure** ([Industrial Empathy](https://www.industrialempathy.com/posts/design-docs-at-google/); [Pragmatic Engineer](https://newsletter.pragmaticengineer.com/p/software-engineering-rfc-and-design)):
- **Context and scope** — succinct background facts (not a requirements doc).
- **Goals and non-goals** — and note that non-goals are *reasonable* goals you explicitly chose to exclude (e.g., "ACID compliance: non-goal"), not "shouldn't crash."
- **The actual design** — overview then detail. *This is the place to write down the trade-offs.*
- **System-context diagram**, **APIs** (sketch, don't paste verbose definitions), **data storage**, pseudo-code only for novel algorithms.
- **Degree of constraint.**
- ⭐ **Alternatives considered** — one of the most important sections: the other designs and *why their trade-offs were worse* given the goals.
- **Cross-cutting concerns** — security, privacy, observability.

Key wisdom: the sweet spot is **~10–20 pages** (a focused 1–3 page "mini design doc" is great for incremental work); and if a doc is just an *implementation manual* with no trade-offs or alternatives, you should have written the code instead ([Industrial Empathy](https://www.industrialempathy.com/posts/design-docs-at-google/)). The lifecycle: **create & iterate → review → implement & iterate → maintain** ([Industrial Empathy](https://www.industrialempathy.com/posts/design-docs-at-google/)). Uber's service-RFC template adds SLAs, dependencies, load/perf testing, multi-DC, security, rollout, and metrics — a good checklist for production services ([Pragmatic Engineer](https://newsletter.pragmaticengineer.com/p/software-engineering-rfc-and-design)).

---

## 5. ADR — Architecture Decision Record

A short text file capturing **one architecturally-significant decision** — those affecting structure, non-functional characteristics, dependencies, interfaces, or construction techniques ([Cognitect — Documenting Architecture Decisions](https://www.cognitect.com/blog/2011/11/15/documenting-architecture-decisions)). ADRs are the institutional memory that answers the future question *"why on earth did we do it this way?"*

**Michael Nygard's format** — kept in the repo at `doc/adr/NNN.md`, numbered sequentially and never reused ([Cognitect](https://www.cognitect.com/blog/2011/11/15/documenting-architecture-decisions); [Nygard ADR template](https://github.com/joelparkerhenderson/architecture-decision-record/blob/main/locales/en/templates/decision-record-template-by-michael-nygard/index.md)):
- **Title** — a short noun phrase ("ADR 9: Use Postgres for the primary store").
- **Status** — proposed → accepted → (later) deprecated / **superseded by ADR-N**.
- **Context** — the forces at play (technical, business, political).
- **Decision** — the choice, stated actively ("We will…").
- **Consequences** — the resulting context, listing **positive, negative, and neutral** outcomes — not just the good ones ([Cognitect](https://www.cognitect.com/blog/2011/11/15/documenting-architecture-decisions)).

The genius is its smallness and immutability: when a decision changes, you **don't edit** the old ADR — you write a new one that supersedes it, preserving the historical record ([Cognitect](https://www.cognitect.com/blog/2011/11/15/documenting-architecture-decisions)). The consequences of one ADR become the context of the next.

---

## 6. Choosing & sequencing

A typical flow for a non-trivial feature: **PRD** (why/what, product) → **requirements/SRS** (precise what) → **RFC/Design Doc** (how + trade-offs) → **ADRs** (capture the load-bearing decisions made in the RFC) → implementation. In AI-assisted teams, these collapse into the [SDD artifacts](14-spec-driven-development.md) (`requirements.md`, `design.md`, `tasks.md`) — but the *quality criteria* above are exactly what make those artifacts good.

> **Anti-pattern — documentation theater:** writing documents nobody reads or updates. Write a doc only when it de-risks a decision, coordinates people, or preserves a non-obvious *why*. Keep it the minimum length that does the job, and keep it current — a stale doc actively misleads.

---

## Key sources
- [What is a PRD — Atlassian](https://www.atlassian.com/agile/product-management/requirements) · [PRD examples — r/ProductManagement](https://www.reddit.com/r/ProductManagement/comments/r5q2iq/does_anyone_have_example_prds/).
- [Design Docs at Google — Industrial Empathy](https://www.industrialempathy.com/posts/design-docs-at-google/) · [RFC & Design Doc examples — Pragmatic Engineer](https://newsletter.pragmaticengineer.com/p/software-engineering-rfc-and-design).
- [Documenting Architecture Decisions — Cognitect (Nygard)](https://www.cognitect.com/blog/2011/11/15/documenting-architecture-decisions) · [ADR template](https://github.com/joelparkerhenderson/architecture-decision-record/blob/main/locales/en/templates/decision-record-template-by-michael-nygard/index.md).
- [Functional Specification Document template — Stanford](https://uit.stanford.edu/sites/default/files/2017/08/30/Functional%20Specification%20Document%20Template.docx) · [How to Write an FDD — Imperium Dynamics](https://imperiumdynamics.com/blog/How-to-Write-a-Functional-Design-Document.html) · [FDD/TDD — Microsoft Learn](https://learn.microsoft.com/en-us/dynamics365/guidance/patterns/create-functional-technical-design-document).
