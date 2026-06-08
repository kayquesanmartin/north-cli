# 16 — Diagramming & Visual Modeling (C4, UML, ERD)

A diagram is a compression algorithm for understanding — it conveys structure faster than prose. But most architecture diagrams fail because they mix abstraction levels, invent ad-hoc notation, and rot the moment they're drawn. This file covers the three notations worth knowing — **C4** (the modern default for software architecture), **UML** (the formal classic, used selectively), and **ER diagrams** (for data models) — and how to use them without producing wall art nobody trusts.

---

## 1. C4 — the modern default for architecture diagrams

The **C4 model** (Simon Brown) describes software architecture at **four hierarchical levels of abstraction**, like zooming a map from country to street ([c4model.com](https://c4model.com)):

1. **Context** — the system as a single box, surrounded by its users and the other systems it talks to. For non-technical and technical audiences alike: *who uses it and what does it integrate with?*
2. **Container** — zoom into the system: the deployable/runnable units — web app, API, database, message broker, SPA. **"Container" here means a runtime, not Docker.** Shows the major tech choices and how containers communicate.
3. **Component** — zoom into one container: its major structural building blocks and their responsibilities/interactions (maps well onto your [Clean Architecture](01-architecture-principles.md) layers).
4. **Code** — zoom into one component: UML class diagrams etc. Usually skipped or auto-generated — it rots fastest and the IDE shows it better.

Why C4 wins for most teams:
- **It's notation-independent and abstraction-first.** It tells you *what to draw at each zoom level*, not which shapes to use — eliminating the "every box and line means something different" problem.
- **Audience-matched.** You show the Context diagram to stakeholders and the Component diagram to engineers, instead of one incomprehensible mega-diagram.
- **The Context and Container diagrams alone cover ~80% of real communication needs.** Start there; go deeper only when a specific container is complex.
- It pairs naturally with the [design doc's "system-context diagram"](15-engineering-documents.md) that Google recommends.

Tooling: hand-drawn is fine; **Structurizr** (Brown's tool) and **Mermaid C4** let you keep diagrams as code/text next to the source so they version and update with it.

---

## 2. UML — the formal classic, used surgically

UML (Unified Modeling Language) is a comprehensive standard whose 14 diagram types split into **structure diagrams** (static) and **behavior diagrams** (dynamic) ([uml-diagrams.org — UML 2.5 overview](https://www.uml-diagrams.org/uml-25-diagrams.html)). Almost nobody uses all of it; a senior engineer uses **four or five** types where they add clarity ([Creately — UML diagram types](https://creately.com/blog/diagrams/uml-diagram-types-examples/)):

- ⭐ **Sequence diagram** — objects/services exchanging messages over time (lifelines + arrows). The single most useful UML diagram for backend work: it makes request flows, async messaging, and saga choreography legible. Kiro's `design.md` explicitly uses sequence diagrams ([file 14](14-spec-driven-development.md)) ([IBM Developer — sequence diagram](https://developer.ibm.com/articles/the-sequence-diagram/)).
- **Class diagram** — classes, attributes, and relationships (association, inheritance, composition). Useful for modeling a [DDD aggregate](02-domain-driven-design.md) or a complex domain model; don't diagram trivial classes.
- **Use case diagram** — actors and the use cases they perform; good in an [FSD/requirements doc](15-engineering-documents.md) to scope behavior ([Creately](https://creately.com/blog/diagrams/uml-diagram-types-examples/)).
- **Activity diagram** — flowchart of a workflow/business process, with branches and parallelism. Good for documenting a multi-step process or saga.
- **State machine diagram** — discrete states and transitions of an entity (e.g., an `Order`'s lifecycle); invaluable when behavior is state-dependent ([uml-diagrams.org](https://www.uml-diagrams.org/uml-25-diagrams.html)).

> **Senior stance:** UML's value today is mostly **sketching to communicate**, not exhaustive code-generating models. Use the diagram type that clarifies the specific thing you're explaining, keep it informal, and don't be precious about full conformance to the spec.

---

## 3. ER Diagrams — modeling the data

The **Entity-Relationship Diagram (ERD)** models the data structure: **entities** (nouns → tables), **attributes** (columns), and **relationships** with **cardinality** (one-to-one, one-to-many, many-to-many) ([Lucidchart — ER diagrams](https://www.lucidchart.com/pages/er-diagrams)). It's the visual companion to [database design](17-database-design.md) and the normalization work in [file 08](08-databases.md).

ERDs exist at three levels of detail ([Visual Paradigm — ERD guide](https://www.visual-paradigm.com/guide/data-modeling/what-is-entity-relationship-diagram/); [Lucidchart](https://www.lucidchart.com/pages/er-diagrams)):
- **Conceptual** — high-level entities and relationships; no attributes/keys. For business discussion.
- **Logical** — entities, attributes, keys, normalized; technology-agnostic.
- **Physical** — actual tables, columns, data types, indexes, constraints — ready to generate the schema.

A practical drawing workflow ([Visual Paradigm](https://www.visual-paradigm.com/guide/data-modeling/what-is-entity-relationship-diagram/)):
1. Fix the **purpose** (business model vs. DB-ready) and **scope** (avoids redundant entities).
2. Draw the **major entities**, then add **attributes** (columns).
3. Review whether the entities/columns can actually **store all the data** the system needs; add transactional/operational/event entities as discovered.
4. Connect entities with relationships and **proper cardinality** (e.g., Customer 1—* Order).
5. Apply **normalization** to reduce redundancy and improve integrity ([file 08](08-databases.md)).

Crow's-foot notation is the common standard for cardinality. Watch for redundant entities/relationships and missing attributes when troubleshooting ([Lucidchart](https://www.lucidchart.com/pages/er-diagrams)).

---

## 4. Diagrams that age well

- **Diagrams as code** — Mermaid, PlantUML, D2, Structurizr DSL. Text-based diagrams live in the repo, diff in PRs, and update with the code. This is the antidote to diagram rot; prefer it for anything that must stay accurate.
- **One abstraction level per diagram** — the C4 discipline. Mixing levels is the #1 readability killer.
- **A legend if notation isn't standard**; better, use a standard so you don't need one.
- **Draw the few diagrams that get looked at**, not a complete model. A correct Context + Container + one Sequence diagram beats a 40-diagram UML model nobody opens.
- **Date or version them**, and delete diagrams you won't maintain — a wrong diagram is worse than none.

---

## Key sources
- [The C4 model — Simon Brown](https://c4model.com) and [simonbrown.je](https://simonbrown.je) ([AMA](https://www.reddit.com/r/softwarearchitecture/comments/1oos3oe/ama_with_simon_brown_creator_of_the_c4_model/)).
- [UML 2.5 Diagrams Overview — uml-diagrams.org](https://www.uml-diagrams.org/uml-25-diagrams.html) · [UML diagram types with examples — Creately](https://creately.com/blog/diagrams/uml-diagram-types-examples/) · [The sequence diagram — IBM Developer](https://developer.ibm.com/articles/the-sequence-diagram/).
- [What is an ERD — Lucidchart](https://www.lucidchart.com/pages/er-diagrams) · [ERD guide — Visual Paradigm](https://www.visual-paradigm.com/guide/data-modeling/what-is-entity-relationship-diagram/).
