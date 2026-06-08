# 02 — Domain-Driven Design (DDD)

DDD is the discipline of letting the **business domain**, not the database or the framework, drive the design of software. It splits into **strategic** design (how to carve a large system into autonomous parts) and **tactical** design (how to model the inside of one part). For backend engineers building distributed systems, the strategic half is the one that pays the rent — it tells you *where to draw service boundaries*.

---

## 1. Ubiquitous Language

The foundation. The team — engineers *and* domain experts — builds a single, rigorous, shared vocabulary, and that exact vocabulary appears in the code (class names, methods, events). When a domain expert says "a *policy* is *renewed*," there is a `Policy` with a `renew()` method. Ambiguity in language is ambiguity in the model, which becomes bugs.

---

## 2. Bounded Contexts (the central strategic pattern)

A **Bounded Context** is an explicit boundary within which a particular model and its ubiquitous language are consistent and valid ([Martin Fowler — Bounded Context](https://martinfowler.com/bliki/BoundedContext.html)). The same word means different things in different contexts: a "Customer" in the Sales context (leads, pipeline) is a different model from a "Customer" in the Billing context (invoices, payment methods). Trying to build one universal `Customer` class for the whole enterprise is the classic failure mode — it becomes a god-object that every team fights over.

> Eric Evans' guidance: make the boundaries explicit, and define how models relate at the seams ([Eric Evans, DDD Europe 2020 — Bounded Contexts](https://www.youtube.com/watch?v=am-HXycfalo)).

**Context Mapping** describes the relationships between contexts:
- **Partnership** / **Shared Kernel** — two contexts cooperate, sharing a small model.
- **Customer–Supplier** — upstream context serves downstream needs.
- **Conformist** — downstream just accepts upstream's model.
- **Anti-Corruption Layer (ACL)** — downstream translates the upstream model into its own, protecting its domain from a messy external one. *This is one of the most valuable patterns in real integration work.*
- **Open Host Service / Published Language** — a context publishes a well-defined protocol (often an API or event schema) for many consumers.

**Bounded contexts map naturally onto microservice boundaries.** A service per bounded context is a far better decomposition heuristic than "a service per entity" or "a service per table."

---

## 3. Tactical patterns (modeling inside a context)

- **Entity** — an object defined by *identity* and continuity over time (a `User`, an `Order`), not by its attributes.
- **Value Object** — defined entirely by its attributes, immutable, no identity (`Money`, `DateRange`, `Address`). Prefer value objects; they're side-effect-free and trivially testable.
- **Aggregate** — a cluster of entities and value objects treated as a single consistency boundary, with one **Aggregate Root** as the only entry point. Invariants are enforced inside the aggregate. **Rule of thumb:** keep aggregates small; reference other aggregates by ID, not by object reference; one transaction should modify one aggregate.
- **Domain Event** — something that happened in the domain that experts care about (`OrderPlaced`, `PaymentReceived`). The bridge to event-driven architecture ([file 04](04-event-driven-cqrs.md)).
- **Repository** — a collection-like abstraction for retrieving and persisting aggregates, hiding the database. Lives as an *interface* in the domain, implemented in infrastructure (Dependency Inversion — see [file 01](01-architecture-principles.md)).
- **Domain Service** — domain logic that doesn't naturally belong to a single entity/value object (e.g., a transfer between two accounts).
- **Factory** — encapsulates complex aggregate creation.

---

## 4. Why aggregates are the hard part

The aggregate boundary *is* the transactional consistency boundary. Get it wrong and you either:
- make aggregates too big → lock contention, poor concurrency, and you fight the database; or
- make them too small → you need cross-aggregate transactions, which in a distributed system means **sagas** ([file 03](03-microservices.md)) and eventual consistency.

This is where DDD, transaction design, and distributed-systems consistency meet. The senior move is to model aggregates around the *true invariants* — only data that must be consistent *immediately and atomically* belongs in the same aggregate. Everything else can be eventually consistent.

---

## 5. When NOT to do DDD

DDD's full tactical machinery has a real cost. For a CRUD app with thin business logic ("anemic" by nature and that's fine), full DDD is overkill — you'll build aggregates and repositories around what is essentially a spreadsheet. Reserve tactical DDD for **subdomains with genuine complexity** (the "core domain" that differentiates the business). Use simpler approaches for supporting/generic subdomains (and consider buying instead of building those).

---

## Key sources
- Eric Evans — *Domain-Driven Design: Tackling Complexity in the Heart of Software* (the "Blue Book").
- Vaughn Vernon — *Implementing Domain-Driven Design* (the "Red Book"); [sample chapters PDF](https://ptgmedia.pearsoncmg.com/images/9780321834577/samplepages/0321834577.pdf).
- Martin Fowler — [Bounded Context](https://martinfowler.com/bliki/BoundedContext.html).
- Eric Evans — [Bounded Contexts, DDD Europe 2020 (video)](https://www.youtube.com/watch?v=am-HXycfalo).
