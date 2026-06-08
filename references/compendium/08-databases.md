# 08 — Databases & Data Modeling

Your data model is the **hardest thing to change** after launch — application code can be refactored in an afternoon; migrating a 500GB production schema with zero downtime is a project. Choosing and modeling data well is therefore one of the highest-leverage decisions a system-builder makes. Kleppmann's guiding rule: *choose your database not based on hype, but on how your application uses the data* ([Tech World With Milan — DDIA summary](https://newsletter.techworld-with-milan.com/p/what-i-learned-from-the-book-designing)).

---

## 1. Picking a data model

| Need | Model | Why |
|---|---|---|
| ACID transactions, complex joins, strong consistency | **Relational (SQL)** | Still the safe default for transactional systems ([DDIA summary](https://newsletter.techworld-with-milan.com/p/what-i-learned-from-the-book-designing)) |
| Flexible/evolving schema, document-shaped data, write-heavy with eventual consistency | **Document (e.g., MongoDB)** | Schema-on-read, locality of a document |
| Simple lookups by key, caching, sessions | **Key-value (Redis, DynamoDB)** | Lowest latency, trivial horizontal scale |
| Highly interconnected data, many-hop traversals (social graphs, fraud) | **Graph (Neo4j)** | Eliminates the join explosion; traversal is the primitive ([DDIA summary](https://newsletter.techworld-with-milan.com/p/what-i-learned-from-the-book-designing)) |
| Time-series / metrics | **Time-series (TimescaleDB, InfluxDB)** | Optimized for append + time-windowed queries |
| Analytics over huge datasets | **Columnar / OLAP (ClickHouse, BigQuery)** | Column storage + compression for scans |

> **"NoSQL" is not "no schema."** You still have a schema — it's just enforced by your application (schema-on-read) instead of the database (schema-on-write). The flexibility is real, but so is the cost of inconsistent data when the application forgets the rules.

**Polyglot persistence** — using different stores for different needs within one system — is legitimate, but each store you add is operational burden (backups, monitoring, expertise). Don't add a graph DB for one feature you could model relationally.

---

## 2. Relational modeling & normalization

**Normalization** organizes data to eliminate redundancy and update anomalies:
- **1NF** — atomic values, no repeating groups.
- **2NF** — no partial dependency on part of a composite key.
- **3NF** — no transitive dependencies; every non-key attribute depends only on the key.
- (BCNF, 4NF, 5NF for stricter cases.)

**Denormalization** is the deliberate reintroduction of redundancy to speed reads (precomputed totals, duplicated fields). It trades write complexity and consistency risk for read performance. **Normalize until it hurts, denormalize until it works** — and only when you have measured a real read bottleneck.

---

## 3. ACID — the transactional guarantees

ACID is the contract a transactional database makes ([Memgraph — ACID & isolation](https://memgraph.com/blog/acid-transactions-meaning-of-isolation-levels)):
- **Atomicity** — all-or-nothing; a transaction's changes commit fully or not at all. Pull the plug mid-transaction and you never see a partial result.
- **Consistency** — the database moves from one valid state to another, honoring constraints (ranges, uniqueness, foreign keys).
- **Isolation** — concurrent transactions behave as if they ran independently — critical for multi-user systems.
- **Durability** — once committed, changes survive crashes (written to durable storage / WAL).

Kleppmann's nuance: people claim you must abandon transactions for performance/scale, but that's overstated — multi-object transactions are harder in distributed settings, yet transactions remain critical for many correctness guarantees ([DDIA summary](https://newsletter.techworld-with-milan.com/p/what-i-learned-from-the-book-designing)).

---

## 4. Isolation levels — where correctness quietly breaks

Isolation is a spectrum trading consistency against concurrency/performance ([GeeksforGeeks — Isolation levels](https://www.geeksforgeeks.org/dbms/transaction-isolation-levels-dbms/)). The ANSI levels and the anomalies they permit:

| Level | Dirty read | Non-repeatable read | Phantom read |
|---|---|---|---|
| **Read Uncommitted** | ✗ allowed | ✗ allowed | ✗ allowed |
| **Read Committed** | prevented | ✗ allowed | ✗ allowed |
| **Repeatable Read** | prevented | prevented | ✗ allowed |
| **Serializable** | prevented | prevented | prevented |

- **Dirty read** — seeing another transaction's *uncommitted* writes.
- **Non-repeatable read** — re-reading a row yields different committed values.
- **Phantom read** — re-running a query returns new rows that match.

Higher isolation = stronger correctness, lower concurrency, slower ([GeeksforGeeks](https://www.geeksforgeeks.org/dbms/transaction-isolation-levels-dbms/)). Beyond ANSI:
- **Snapshot Isolation** — each transaction sees a consistent snapshot as of its start; great concurrency, but vulnerable to **write skew** ([Memgraph](https://memgraph.com/blog/acid-transactions-meaning-of-isolation-levels)).
- **MVCC (Multi-Version Concurrency Control)** — keeps multiple versions of rows so readers don't block writers (how Postgres and others implement snapshot isolation) ([Memgraph](https://memgraph.com/blog/acid-transactions-meaning-of-isolation-levels)).

**The race conditions Kleppmann highlights** ([DDIA summary](https://newsletter.techworld-with-milan.com/p/what-i-learned-from-the-book-designing)):
- **Lost update** — two transactions overwrite each other. Fix with atomic operations, explicit locks, or compare-and-set (optimistic concurrency).
- **Write skew / phantoms** — concurrent updates that each individually look valid but jointly violate an invariant. Requires serializable isolation.

> **Default trap:** know your database's *default* isolation level (often Read Committed) and whether it's strong enough for your invariants. Many subtle production bugs are isolation-level bugs that only appear under concurrency. The seminal reference is *A Critique of ANSI SQL Isolation Levels* (Berenson et al.) ([Memgraph](https://memgraph.com/blog/acid-transactions-meaning-of-isolation-levels)).

---

## 5. Indexing — the performance lever

- An index is a separate data structure (usually a **B-tree**, sometimes a **hash** or **LSM-tree**) that speeds reads at the cost of slower writes and more storage.
- **Composite indexes** are order-sensitive: an index on `(a, b)` helps `WHERE a = ? AND b = ?` and `WHERE a = ?`, but not `WHERE b = ?` alone (the "leftmost prefix" rule).
- **Covering index** — includes all columns a query needs, so the DB never touches the table.
- Learn to read **`EXPLAIN`/`EXPLAIN ANALYZE`** — it's the single most useful database performance skill. Watch for sequential scans on large tables, and for indexes that exist but aren't used.
- **B-tree vs LSM-tree:** B-trees (most SQL DBs) favor read-optimized, in-place updates; LSM-trees (Cassandra, RocksDB) favor write-heavy workloads via append + compaction. This is a core DDIA storage-engine distinction.

---

## 6. Practical senior concerns

- **Migrations** must be backward-compatible and run online: expand → migrate → contract. Never a destructive change in one deploy.
- **N+1 query problem** — the most common ORM performance killer; eager-load or batch.
- **Connection pooling** — databases have hard connection limits; pool and bound them, especially with many service instances.
- **Don't put business logic the domain owns into the database** unless you've consciously chosen a DB-centric architecture — it fragments your domain model across two languages.

---

## Key sources
- Martin Kleppmann — *Designing Data-Intensive Applications* ([free PDF mirror](https://0-lucas.github.io/digital-garden/99.-Books/Martin-Kleppmann---Designing-Data-Intensive-Applications_-O%E2%80%99Reilly-Media-(2017).pdf); [summary](https://newsletter.techworld-with-milan.com/p/what-i-learned-from-the-book-designing)).
- [Transaction Isolation Levels — GeeksforGeeks](https://www.geeksforgeeks.org/dbms/transaction-isolation-levels-dbms/).
- [ACID Transactions & Isolation Levels — Memgraph](https://memgraph.com/blog/acid-transactions-meaning-of-isolation-levels).
