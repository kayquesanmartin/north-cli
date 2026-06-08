# 03 — Microservices & Distributed Architecture

Microservices are an architectural style that structures an application as a collection of **independently deployable** services, each owning its data and aligned to a business capability. The promise is autonomous teams, independent scaling, and fault isolation. The cost is that you trade a set of *simple, local* problems (a method call, a transaction) for *hard, distributed* ones (network failure, partial failure, eventual consistency, distributed debugging). **Adopt them to solve organizational and scaling problems, not because they are modern.**

The most complete public catalog of the patterns below is Chris Richardson's [microservices.io pattern language](https://microservices.io/patterns/).

---

## 1. Decomposition: where do the boundaries go?

- **Decompose by business capability / subdomain** — align services with [bounded contexts](02-domain-driven-design.md), not technical layers or database tables.
- **Database per Service** — each service owns its private database; no other service may touch it directly ([microservices.io](https://microservices.io/patterns/)). This is what makes services independently deployable — and what makes cross-service data consistency hard.
- The alternative, **Shared Database**, is listed as a pattern but is usually an anti-pattern in disguise: it recouples services at the data layer, defeating the point.

---

## 2. Managing data across services

Because each service owns its data, you lose ACID transactions that span services. Two patterns dominate:

### Saga
A sequence of **local transactions**, one per service, coordinated to maintain consistency across services. If a step fails, the saga runs **compensating transactions** to undo prior steps ([microservices.io](https://microservices.io/patterns/)). Two flavors:
- **Choreography** — services react to each other's events, no central coordinator. Decoupled but the overall flow is implicit and hard to follow ([Confluent — Saga pattern ft. Chris Richardson](https://developer.confluent.io/learn-more/podcasts/choreographing-the-saga-pattern-in-microservices-ft-chris-richardson/)).
- **Orchestration** — a central orchestrator tells each service what to do. The flow is explicit and observable, at the cost of a coordinator component.

> Sagas give you **eventual consistency**, not atomicity. You must design for intermediate, partially-completed states being visible.

### Querying across services
- **API Composition** — a composer invokes the services that own the data and joins in memory. Simple, but inefficient for large joins.
- **CQRS / Command-side replica** — maintain a query-optimized read model fed by events ([file 04](04-event-driven-cqrs.md)).

---

## 3. Communication styles

- **Remote Procedure Invocation (RPI)** — synchronous request/response (gRPC, REST). Simple mental model, but couples availability: if a downstream service is down, you're down. See [API Design](11-api-design.md).
- **Messaging** — asynchronous events/commands via a broker (NATS/JetStream, RabbitMQ, Kafka). Decouples services in time and improves resilience, at the cost of eventual consistency and harder debugging.
- **Idempotent Consumer** — ensure a consumer can be invoked multiple times with the same message without ill effect ([microservices.io](https://microservices.io/patterns/)). Essential because most brokers deliver *at-least-once* ([file 04](04-event-driven-cqrs.md)).

---

## 4. The external edge

- **API Gateway** — a single entry point that gives each client a unified interface, handling routing, auth, rate-limiting, and aggregation ([microservices.io](https://microservices.io/patterns/)).
- **Backend for Frontend (BFF)** — a separate gateway per client type (web, mobile), so each gets a tailored API.

---

## 5. Service discovery

How does a caller find a service instance's network location?
- **Client-side discovery** — the client queries a **Service Registry** and load-balances itself.
- **Server-side discovery** — a router/load balancer queries the registry (e.g., Kubernetes Service + kube-proxy).
- **Self-registration** vs **3rd-party registration** — who writes to the registry ([microservices.io](https://microservices.io/patterns/)).

---

## 6. Resilience: stopping failure from cascading

- **Circuit Breaker** — invoke a remote service via a proxy that *fails fast* once the failure rate crosses a threshold, giving the downstream time to recover and preventing thread-pool exhaustion upstream ([microservices.io](https://microservices.io/patterns/)).
- **Bulkhead** — isolate resources (thread pools, connection pools) per dependency so one slow dependency can't sink the whole service.
- **Retry with backoff + jitter** — retry transient failures, but with exponential backoff and randomized jitter to avoid retry storms. Combine with idempotency.
- **Timeouts everywhere** — an unbounded wait is a latent outage.

---

## 7. Cross-cutting concerns

- **Microservice Chassis / Service Template** — a framework or starter that bakes in logging, metrics, tracing, config, and health checks so every new service starts consistent ([microservices.io](https://microservices.io/patterns/)).
- **Externalized Configuration** — never bake DB locations or credentials into the image; inject them ([12-factor](12-scalability-reliability.md)).
- **Distributed Tracing** — assign each external request a unique trace ID, propagate it across services, and record spans centrally so you can reconstruct a request's path ([microservices.io](https://microservices.io/patterns/)). Non-negotiable for debugging microservices.

---

## 8. The honest trade-off

What you gain: independent deployability, fault isolation, independent scaling, team autonomy, polyglot freedom.

What you pay: network latency and unreliability, eventual consistency, distributed transactions become sagas, far harder testing and debugging, operational complexity (orchestration, service mesh, observability), and the need for real DevOps maturity.

> **Senior rule:** Start with a well-modularized monolith. Extract a microservice when you have a *proven, stable boundary* and a *concrete reason* (independent scaling, independent deploy cadence, or team ownership) — not before.

---

## Key sources
- Chris Richardson — [microservices.io pattern language](https://microservices.io/patterns/) and the book *Microservices Patterns*.
- [Choreographing the Saga Pattern ft. Chris Richardson — Confluent](https://developer.confluent.io/learn-more/podcasts/choreographing-the-saga-pattern-in-microservices-ft-chris-richardson/).
- Sam Newman — *Building Microservices* (2nd ed.), the best end-to-end treatment (see [file 13](13-reading-list.md)).
