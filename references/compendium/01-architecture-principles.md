# 01 — Architecture Principles & Styles

Architecture is the set of decisions that are **expensive to change later**. The job of an architect is not to pick a fashionable style, but to defer and protect those expensive decisions so the system can evolve. The unifying idea behind every "good" architecture below is the same: **isolate the business rules from the delivery mechanisms (UI, DB, frameworks) so that the things that change often cannot force changes in the things that change rarely.**

---

## 1. The core principle: dependencies point toward stability

The single most important rule across Clean, Onion, and Hexagonal architectures is the **Dependency Rule**: source-code dependencies may only point *inward*, toward higher-level policy. Nothing in an inner circle may name anything in an outer circle ([Robert C. Martin, "The Clean Architecture"](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)).

The layers, from inside out:

- **Entities (Domain)** — enterprise-wide business rules. The most stable, most abstract code. No knowledge of databases, frameworks, or HTTP.
- **Use Cases (Application)** — application-specific business rules; orchestrate entities to fulfill a user goal.
- **Interface Adapters** — controllers, presenters, gateways, repositories: translate between use cases and the outside world.
- **Frameworks & Drivers** — the web framework, the database, the message broker. The most volatile, lowest-level detail ([cubic.dev — dependency rules](https://www.cubic.dev/blog/how-to-maintain-clean-architecture-with-dependency-rules-in-your-codebase)).

When control flow must run *outward* (e.g., a use case needs to call a presenter, or persist via a database), but the dependency must point *inward*, you resolve the contradiction with the **Dependency Inversion Principle**: the inner layer declares an interface (an "output port"), and the outer layer implements it. You use polymorphism to make the source-code dependency oppose the flow of control ([Uncle Bob](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)).

> **Why this matters:** It makes the domain testable without a UI, DB, or web server, and lets you swap Oracle for Postgres, or REST for gRPC, without touching business rules ([Uncle Bob](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)).

---

## 2. The styles, compared

### Layered (n-tier)
The classic Presentation → Business → Persistence → Database stack. Simple, universally understood, and the right default for many CRUD apps.
- **Trap:** layers often leak — the persistence model bleeds into the UI, and "business logic" ends up in stored procedures and controllers. The dependency arrow frequently points the *wrong* way (domain depends on the ORM).

### Hexagonal (Ports & Adapters) — Alistair Cockburn
The application sits at the center, surrounded by **ports** (interfaces describing what the app needs/offers) and **adapters** (concrete implementations: a REST adapter, a Postgres adapter, a Kafka adapter). The intent: *"Allow an application to equally be driven by users, programs, automated test, or batch scripts, and to be developed and tested in isolation from its eventual run-time devices and databases"* ([Alistair Cockburn — Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture)).
- Cockburn deliberately chose a hexagon to suggest there are a *limited* number of ports — he advocates keeping ports few (ideally fewer than four), not literally six ([r/softwarearchitecture discussion](https://www.reddit.com/r/softwarearchitecture/comments/1pb9zge/i_finally_understood_hexagonal_architecture_after/)).

### Onion / Clean
Refinements of the same idea with named concentric rings. Onion popularized domain-centric layering; Clean (Uncle Bob) added the explicit four rings and the input/output port vocabulary. In practice **Hexagonal, Onion, and Clean are the same family** — they all enforce the Dependency Rule via inversion ([bitloops — Clean Architecture](https://bitloops.com/docs/bitloops-language/learning/software-architecture/clean-architecture)).

### Modular Monolith
A single deployable unit, but internally partitioned into modules with enforced boundaries (each module owns its data, exposes a narrow interface). This is the **correct default** for most teams: you get clean boundaries without the operational tax of distribution. You can extract a module into a service *later*, once a boundary has proven stable and a real scaling/ownership need exists.

### Microservices
Independently deployable services aligned to business capabilities. Covered in depth in [file 03](03-microservices.md). Treat them as a solution to **organizational and scaling problems**, not as a default.

---

## 3. Choosing: a decision heuristic

| Signal | Lean toward |
|---|---|
| Small team, single product, unproven domain | Modular monolith, layered |
| Rich domain logic, complex invariants | Clean/Hexagonal + DDD |
| Independent scaling, autonomous teams, polyglot persistence | Microservices |
| Heavy audit / temporal requirements, complex read/write asymmetry | Event Sourcing + CQRS ([file 04](04-event-driven-cqrs.md)) |

**Anti-pattern — "architecture astronautics":** adopting hexagonal + CQRS + microservices on day one for a CRUD app. Every boundary you add is a tax on every future change. Add boundaries when the pain of *not* having them is real and present, not anticipated.

---

## 4. Cross-cutting architectural concerns

- **Conway's Law:** your system's structure will mirror your org's communication structure. If you want a modular system, structure your teams modularly first.
- **Coupling & cohesion** are the real metrics behind every "ility." High cohesion within a module, low coupling between modules.
- **Fitness functions:** encode architectural rules (e.g., "the domain layer must not import the web framework") as automated tests, so the architecture doesn't erode silently (see *Building Evolutionary Architectures*, [file 13](13-reading-list.md)).

---

## Key sources
- Robert C. Martin — [The Clean Architecture (blog)](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html) and the book *Clean Architecture*.
- Alistair Cockburn — [Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture).
- [Clean Architecture explained — bitloops](https://bitloops.com/docs/bitloops-language/learning/software-architecture/clean-architecture).
- See the full ranked list in [file 13](13-reading-list.md).
