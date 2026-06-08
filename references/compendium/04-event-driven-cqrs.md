# 04 — Event-Driven Architecture, Event Sourcing & CQRS

These three are distinct ideas that are frequently combined. Given your background in NATS/JetStream, RabbitMQ, and event-driven systems, this is the file where the abstract architecture meets the broker you actually operate.

---

## 1. Event-Driven Architecture (EDA)

In EDA, components communicate by **producing and reacting to events** rather than calling each other directly. An event is an immutable statement that *something happened* (`OrderPlaced`). Producers don't know who consumes; consumers don't know who produced. This yields **temporal decoupling** (producer and consumer needn't be up at the same time) and easy extensibility — add a new consumer without touching producers ([DEV — EDA, Event Sourcing & CQRS](https://dev.to/yasmine_ddec94f4d4/event-driven-architecture-event-sourcing-and-cqrs-how-they-work-together-1bp1)).

**Events vs. Commands:** a *command* is an intent directed at a specific handler ("do this"); an *event* is a fact broadcast to anyone interested ("this happened"). Keep them distinct in your schema and naming.

**Trade-off:** you gain decoupling and scalability but lose the easy, linear traceability of a synchronous call. Reasoning about *global* behavior becomes harder, and you must invest in observability and tracing.

---

## 2. Delivery semantics — the thing you must get right

No broker gives you magic. There are three semantics ([ByteByteGo — At most/least/exactly once](https://blog.bytebytego.com/p/at-most-once-at-least-once-exactly)):

| Semantic | Guarantee | Use when |
|---|---|---|
| **At-most-once** | Maybe lost, never duplicated. No ACK/retry. | Metrics, telemetry where loss is acceptable |
| **At-least-once** | Never lost, possibly duplicated. Broker retries until ACK. | The realistic default for RabbitMQ, SQS, Kafka, JetStream |
| **Exactly-once** | No loss, no duplication. | Desirable, expensive, and *end-to-end across heterogeneous services it is effectively unachievable* |

**The practical truth:** most production systems achieve *effective* exactly-once by combining **at-least-once delivery + idempotent consumers** ([DEV — Inbox Pattern](https://dev.to/actor-dev/inbox-pattern-51af)). Kafka offers transactional/idempotent producers, but true end-to-end exactly-once across services is extremely hard to guarantee ([ByteByteGo](https://blog.bytebytego.com/p/at-most-once-at-least-once-exactly)).

---

## 3. Idempotency, Outbox & Inbox — the reliability triad

These patterns are what make event-driven systems correct in the presence of retries and crashes.

### The dual-write problem
If a service writes to its database *and* publishes an event as two separate operations, a crash between them leaves the system inconsistent (DB updated, event lost — or vice versa). You cannot wrap a DB write and a broker publish in one transaction.

### Outbox pattern (producer side)
Write the event into an `outbox` table **in the same local transaction** as the business state change. A separate relay process polls (or tails the change log of) the outbox and publishes to the broker, marking rows as sent. The DB transaction guarantees the event is recorded atomically with the state change; the relay guarantees it eventually reaches the broker (at-least-once) ([OneUptime — exactly-once delivery](https://oneuptime.com/blog/post/2026-01-30-exactly-once-delivery/view)).

### Inbox pattern (consumer side)
The consumer records every processed message's unique ID in an `inbox` table. Before processing, it checks whether the ID was already handled; if so, it skips. This turns an at-least-once stream into idempotent processing, and also lets you ACK a "poison" message to unblock a queue and replay later ([DEV — Inbox Pattern](https://dev.to/actor-dev/inbox-pattern-51af)).

### Implementation guidelines
- Always attach a unique **message/correlation ID** to every event.
- Set sensible **TTLs** on idempotency/dedup keys.
- Route repeatedly-failing messages to a **Dead Letter Queue (DLQ)**.
- Monitor duplicate rates — a high rate signals an upstream bug.
- **Test failure explicitly** — kill services mid-transaction and verify recovery ([OneUptime](https://oneuptime.com/blog/post/2026-01-30-exactly-once-delivery/view)).

---

## 4. Event Sourcing

Instead of storing only the *current* state, you store the **full, ordered, append-only sequence of events** that produced it. Current state is derived by replaying events ([Mia-Platform — Event Sourcing & CQRS](https://mia-platform.eu/blog/understanding-event-sourcing-and-cqrs-pattern/)).

Core concepts ([Mia-Platform](https://mia-platform.eu/blog/understanding-event-sourcing-and-cqrs-pattern/)):
- **Events** — immutable records of each change (`OrderPlaced`, `PaymentProcessed`, `OrderShipped`).
- **Streams** — the ordered sequence of events for one entity/aggregate.
- **Projections** — read models built by folding over events (e.g., total revenue, current inventory).

**Design events around business intent, not state deltas.** Record "two seats were reserved," not "remaining seats changed to 42." Intent-focused events give you meaningful audit trails and the freedom to build *new* read models from history later, without changing the write side ([Azure Architecture Center — Event Sourcing](https://learn.microsoft.com/en-us/azure/architecture/patterns/event-sourcing)).

**Benefits:** complete audit log "for free," temporal queries (state at any past point), natural fit for horizontal scaling and async processing, and it sidesteps direct-update conflicts because the store is append-only ([Azure](https://learn.microsoft.com/en-us/azure/architecture/patterns/event-sourcing); [Mia-Platform](https://mia-platform.eu/blog/understanding-event-sourcing-and-cqrs-pattern/)).

**Costs / traps:** schema/versioning of old events is genuinely hard; rebuilding projections over millions of events needs **snapshots**; eventual consistency of read models; and the entire team must understand it or they'll "just add an UPDATE." It is the right tool for domains with strong **audit/temporal/regulatory** needs — and overkill almost everywhere else.

---

## 5. CQRS (Command Query Responsibility Segregation)

Separate the **write model** (commands that change state) from the **read model** (queries) — potentially with separate data stores, scaled independently ([Mia-Platform](https://mia-platform.eu/blog/understanding-event-sourcing-and-cqrs-pattern/)).

- It is an **architectural separation** of read/write responsibilities — distinct from Event Sourcing, which is about *how state is persisted* ([Mia-Platform](https://mia-platform.eu/blog/understanding-event-sourcing-and-cqrs-pattern/)).
- They pair naturally: the write side appends events; projections materialize query-optimized read views. The presentation layer writes commands to command handlers and reads from a separate read store ([Azure Architecture Center](https://learn.microsoft.com/en-us/azure/architecture/patterns/event-sourcing)).
- **Why:** independently scale reads vs. writes; append-only ingestion and query-optimized projections run separately, avoiding lock contention ([Azure](https://learn.microsoft.com/en-us/azure/architecture/patterns/event-sourcing)).

**Trap:** CQRS doubles your models and introduces eventual consistency between write and read sides. Don't apply it system-wide. Apply it to the *specific aggregates* where read/write asymmetry or scaling actually justifies it.

---

## Key sources
- [Event Sourcing pattern — Azure Architecture Center](https://learn.microsoft.com/en-us/azure/architecture/patterns/event-sourcing).
- [Understanding Event Sourcing and CQRS — Mia-Platform](https://mia-platform.eu/blog/understanding-event-sourcing-and-cqrs-pattern/).
- [At-most/least/exactly once — ByteByteGo (Alex Xu)](https://blog.bytebytego.com/p/at-most-once-at-least-once-exactly).
- [The Inbox Pattern — DEV](https://dev.to/actor-dev/inbox-pattern-51af) · [Exactly-once delivery — OneUptime](https://oneuptime.com/blog/post/2026-01-30-exactly-once-delivery/view).
- Martin Kleppmann — *Designing Data-Intensive Applications* (stream processing chapters), [file 13](13-reading-list.md).
