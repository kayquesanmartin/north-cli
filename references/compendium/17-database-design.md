# 17 — Database Design in Practice

[File 08](08-databases.md) covered the *theory* (models, ACID, isolation, indexing); [file 09](09-distributed-data.md) covered *distribution*. This file is the **practical workflow** of going from a problem to a production schema — the craft of data modeling — plus the operational realities (migrations, performance, anti-patterns) that bite teams in production.

---

## 1. The three modeling levels

Design top-down through three levels of an [ER model](16-diagramming.md) ([Lucidchart](https://www.lucidchart.com/pages/er-diagrams); [Visual Paradigm](https://www.visual-paradigm.com/guide/data-modeling/what-is-entity-relationship-diagram/)):

1. **Conceptual** — what entities exist and how they relate, in business terms. No keys, no types. Output: agreement with domain experts (ties to [DDD's ubiquitous language](02-domain-driven-design.md)).
2. **Logical** — entities, attributes, primary/foreign keys, relationships with cardinality, normalized. Still technology-agnostic.
3. **Physical** — concrete tables, columns, data types, indexes, constraints, partitions for a specific engine. This generates the DDL.

Designing through these levels prevents two failures: jumping straight to tables (and baking in a bad structure) and over-modeling (entities you'll never store).

---

## 2. Keys & identity

- **Primary key** — choose a **surrogate key** (a synthetic `id`) over a natural key in most transactional systems: natural keys (email, SSN) change and leak business meaning into foreign keys everywhere.
- **Surrogate key type — the real trade-off:**
  - **Auto-increment integer (`bigint`)** — compact, sequential (great for B-tree locality), but reveals row counts and is awkward to generate before insert / across shards.
  - **UUID v4 (random)** — globally unique, generatable client-side, shard-friendly, but random ordering causes B-tree **index fragmentation** and page splits on insert-heavy tables.
  - **UUID v7 / ULID (time-ordered)** — the modern sweet spot: globally unique *and* roughly sequential, so you get distribution-friendliness without trashing index locality. Prefer these for new distributed systems.
- **Foreign keys** enforce referential integrity at the DB level. Keep them on in monoliths. In a [microservices "database per service"](03-microservices.md) world, cross-service FKs are impossible — integrity moves to the application and [sagas](04-event-driven-cqrs.md).

---

## 3. Normalization vs. denormalization — the practical line

Normalize to **3NF** by default ([file 08](08-databases.md)): it eliminates update anomalies and is the correct, safe baseline for transactional (OLTP) systems. Denormalize **deliberately and locally** only when:
- you've **measured** a real read bottleneck a normalized query can't meet;
- the read pattern is hot and the write/consistency cost is acceptable;
- or you're building a separate **read model** ([CQRS](04-event-driven-cqrs.md)) / analytics (OLAP) store, where star/snowflake schemas and wide denormalized tables are *correct by design*.

> **OLTP vs OLAP** is a first-order decision. Transactional workloads (many small reads/writes, strong consistency) want normalized, row-oriented stores. Analytical workloads (big scans, aggregations) want denormalized, column-oriented stores. Don't run heavy analytics on your primary OLTP database — replicate to a warehouse.

---

## 4. Common data-modeling decisions

- **Many-to-many** → a **join/junction table** with the two foreign keys (plus any relationship attributes).
- **Inheritance / polymorphism** → single-table (one table, nullable columns, a type discriminator), class-table (a table per subtype joined to a base), or concrete-table. Each trades query simplicity against null sparsity and integrity.
- **Soft deletes** (`deleted_at`) vs hard deletes — soft deletes preserve history and referential safety but complicate every query and unique constraint; decide consciously.
- **Temporal/audit needs** → audit tables, history tables, or full [event sourcing](04-event-driven-cqrs.md) if the timeline *is* the product.
- **Enums** → DB enum vs lookup table vs check constraint; lookup tables are the most flexible and migration-friendly.
- **JSON columns** — modern SQL engines support them well; great for genuinely schemaless or sparse attributes, dangerous as a dumping ground that hides structure from constraints and indexes. Use for the edges, not the core.

---

## 5. Migrations — changing a live schema safely

Schema changes are the highest-risk routine operation in a running system. The rule: **never a breaking change in one deploy.** Use the **expand → migrate → contract** pattern:
1. **Expand** — add the new column/table (nullable, backward-compatible). Deploy.
2. **Migrate** — backfill data and dual-write from the app; deploy code that reads new, falls back to old.
3. **Contract** — once everything uses the new shape, drop the old column. Deploy.

Operational must-dos: migrations are **versioned and in source control** (Flyway, Liquibase, EF Core Migrations, Prisma); they run as a **separate release step** ([12-factor admin processes](12-scalability-reliability.md)); avoid long-held locks on big tables (use online/`CONCURRENTLY` index builds, batched backfills); and always have a tested rollback or roll-forward plan.

---

## 6. Performance & the usual suspects

- **Index for your query patterns**, not speculatively. Read [`EXPLAIN ANALYZE`](08-databases.md) and watch for sequential scans on large tables, unused indexes, and bad row estimates.
- **The N+1 problem** — an ORM lazy-loading a child per parent row; the most common performance killer. Eager-load or batch.
- **Connection pooling** — DBs have hard connection caps; with many service instances you exhaust them fast. Bound the pool (PgBouncer for Postgres).
- **Pagination** — cursor/keyset pagination scales; `OFFSET` degrades linearly as it skips rows.
- **Avoid `SELECT *`** in hot paths — fetch only needed columns so covering indexes can help and you move less data.
- **Beware over-indexing** — every index slows writes and consumes space; drop unused ones.

---

## 7. Anti-patterns to recognize

- **EAV (Entity-Attribute-Value)** — modeling everything as key/value rows to be "flexible." Destroys type safety, constraints, and query performance. Almost always wrong; use JSON columns or a proper schema instead.
- **The "God table"** — one wide table with 80 nullable columns serving five concepts. Split by concern.
- **Storing derived data without a refresh strategy** — denormalized totals that silently drift out of sync.
- **No constraints** — pushing all integrity to the app "for speed." The database is your last line of defense for data correctness; use NOT NULL, UNIQUE, CHECK, and FK constraints.
- **Premature sharding** — distributing data before a single well-indexed instance is actually saturated. Sharding is a one-way door that complicates everything ([file 09](09-distributed-data.md)).

---

## Key sources
- [What is an ERD — Lucidchart](https://www.lucidchart.com/pages/er-diagrams) · [ERD & data modeling guide — Visual Paradigm](https://www.visual-paradigm.com/guide/data-modeling/what-is-entity-relationship-diagram/).
- [Transaction Isolation Levels — GeeksforGeeks](https://www.geeksforgeeks.org/dbms/transaction-isolation-levels-dbms/) · [ACID & isolation — Memgraph](https://memgraph.com/blog/acid-transactions-meaning-of-isolation-levels).
- Martin Kleppmann — *Designing Data-Intensive Applications* ([summary](https://newsletter.techworld-with-milan.com/p/what-i-learned-from-the-book-designing)); see [file 13](13-reading-list.md).
