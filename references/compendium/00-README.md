# The Senior Engineer's Knowledge Compendium

> A deep, opinionated reference covering the foundational knowledge every developer should master when building real systems — from architecture principles to the operational concerns that keep software alive in production.

This compendium is written at a **senior level**: it favors trade-offs, anti-patterns, and the *why* behind each decision over surface-level definitions. It is meant to be read alongside the primary sources cited throughout — the goal is to give you a mental map and then point you at the canonical material that goes deeper.

---

## How to use this material

1. **Read the roadmap below** to understand how the topics relate.
2. **Start with the layer you're weakest in.** These files are mostly independent; you don't have to read them in order.
3. **Treat the cited books as the real curriculum.** This compendium is the index and the connective tissue; the books are the depth.
4. **Revisit periodically.** Senior judgment comes from re-reading these ideas after you've been burned by ignoring them.

---

## Table of contents

### Part 1 — Core engineering domains

| # | File | Domain |
|---|------|--------|
| 01 | [Architecture Principles & Styles](01-architecture-principles.md) | Layered, Hexagonal, Clean, Onion, modular monolith vs. microservices |
| 02 | [Domain-Driven Design](02-domain-driven-design.md) | Strategic & tactical DDD, bounded contexts, aggregates |
| 03 | [Microservices & Distributed Architecture](03-microservices.md) | Decomposition, sagas, API gateway, service discovery, resilience |
| 04 | [Event-Driven Architecture, Event Sourcing & CQRS](04-event-driven-cqrs.md) | Messaging, delivery semantics, outbox/inbox, idempotency |
| 05 | [Clean Code & SOLID](05-clean-code-solid.md) | Naming, functions, SOLID, cohesion/coupling |
| 06 | [Design Patterns](06-design-patterns.md) | GoF creational/structural/behavioral, when NOT to use them |
| 07 | [Testing Discipline & TDD](07-testing-tdd.md) | TDD, test pyramid, doubles, BDD, contract & property tests |
| 08 | [Databases & Data Modeling](08-databases.md) | Relational vs NoSQL, normalization, ACID, isolation, indexing |
| 09 | [Distributed Data & Consistency](09-distributed-data.md) | CAP, PACELC, replication, partitioning, consensus |
| 10 | [Requirements & Software Engineering Process](10-requirements-process.md) | Elicitation, NFRs, SDLC, Agile, estimation |
| 11 | [API Design](11-api-design.md) | REST, gRPC, GraphQL, versioning, contracts |
| 12 | [Scalability, Reliability & Operations](12-scalability-reliability.md) | 12-factor, caching, observability, SRE, security basics |
| 13 | [Curated Reading List](13-reading-list.md) | The canonical books, docs and papers, ranked |

### Part 2 — Engineering documents (incl. AI-assisted dev) & supplementary essentials

| # | File | Domain |
|---|------|--------|
| 14 | [Spec-Driven Development & AI-Assisted Engineering](14-spec-driven-development.md) | SDD, Spec Kit, Kiro, `AGENTS.md`/`CLAUDE.md`, the Spec→Plan→Tasks→Implement loop |
| 15 | [Engineering Documents](15-engineering-documents.md) | PRD, SRS/Requirements, FSD/FDD, RFC/Design Doc/SDD, ADR |
| 16 | [Diagramming & Visual Modeling](16-diagramming.md) | C4 model, UML (sequence/class/state), ER diagrams |
| 17 | [Database Design in Practice](17-database-design.md) | Modeling levels, keys, normalization, migrations, anti-patterns |
| 18 | [Cybersecurity for Developers](18-cybersecurity.md) | OWASP Top 10, security principles, AuthN/AuthZ, DevSecOps |
| 19 | [Frontend Engineering Essentials](19-frontend.md) | Rendering models, components, state management, Core Web Vitals |

---

## The learning roadmap

Think of system-building knowledge as four concentric concerns. Master them roughly inside-out, but iterate — you'll cycle through all of them on every serious project.

### 1. The core: correctness & expressiveness of code
- **Clean Code & SOLID** (file 05) — write code humans can change.
- **Design Patterns** (file 06) — a shared vocabulary for recurring structures.
- **Testing & TDD** (file 07) — the safety net that makes change cheap.

> Without this layer, everything above it rots. Architecture cannot save a codebase whose individual modules are unreadable and untested.

### 2. The shape: how modules compose into a system
- **Architecture Principles & Styles** (file 01) — dependency direction, boundaries.
- **Domain-Driven Design** (file 02) — aligning software boundaries with business boundaries.
- **API Design** (file 11) — the contracts between modules and services.

### 3. The substrate: data & distribution
- **Databases & Data Modeling** (file 08) — the single hardest thing to change later.
- **Distributed Data & Consistency** (file 09) — what breaks when one box becomes many.
- **Microservices** (file 03) and **Event-Driven/CQRS** (file 04) — distribution as an explicit architecture.

### 4. The lifecycle: getting it built and keeping it alive
- **Requirements & Process** (file 10) — building the right thing, predictably.
- **Scalability, Reliability & Operations** (file 12) — keeping it fast, up, and secure.

---

## A note on judgment

Every pattern in this compendium is a tool with a cost. The senior skill is not knowing patterns — juniors memorize patterns. The senior skill is knowing **when a pattern's benefit exceeds its cost in your specific context**, and having the discipline to choose the boring, simpler option when it does not. Microservices, event sourcing, CQRS, and hexagonal architecture are all guilty of being applied where a well-factored modular monolith with a relational database would have shipped faster and broken less.

> "The competent programmer is fully aware of the limited size of his own skull." — Edsger Dijkstra

Optimize for **deletability and changeability**, not cleverness.

---

*Compiled as a study reference. All external claims are cited inline in each file with links to primary sources.*
