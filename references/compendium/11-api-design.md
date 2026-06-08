# 11 — API Design

An API is a **contract** — and like the data model, a published contract is expensive to change because other people depend on it. Good API design is the discipline of making that contract clear, stable, evolvable, and hard to misuse. For a backend engineer, this is daily work; the choice of *style* (REST/gRPC/GraphQL) has architectural consequences.

---

## 1. The three dominant styles

| | **REST** | **gRPC** | **GraphQL** |
|---|---|---|---|
| Transport / format | HTTP/1.1+, usually JSON | HTTP/2, Protocol Buffers (binary) | HTTP, JSON, single endpoint |
| Contract | OpenAPI (optional, often informal) | `.proto` (strict, code-generated) | SQL-like schema (strict) |
| Strength | Ubiquitous, cacheable, simple, great for public APIs | Very fast, strongly typed, streaming, ideal for internal service-to-service | Client asks for exactly the fields it needs; no over/under-fetching |
| Weakness | Over/under-fetching, many round-trips | Browser support needs a proxy; binary is opaque to debug | Server complexity, caching is hard, easy to write expensive queries |

The consensus guidance ([Red Hat — SOAP/REST/GraphQL/gRPC](https://www.redhat.com/en/blog/apis-soap-rest-graphql-grpc); [Baeldung — REST vs GraphQL vs gRPC](https://www.baeldung.com/rest-vs-graphql-vs-grpc)):
- **REST** — best for public APIs and traditional web apps; proven, low-risk, broad tooling ([LinkedIn — Alex Xu on API styles](https://www.linkedin.com/posts/alexxubyte_systemdesign-coding-interviewtips-activity-7459629754078535680-Frpz)).
- **gRPC** — best for *internal* service-to-service communication and performance-critical, scalable microservices ([LinkedIn](https://www.linkedin.com/posts/alexxubyte_systemdesign-coding-interviewtips-activity-7459629754078535680-Frpz)); it delivers "lightning-fast execution at the expense of flexibility" ([Red Hat](https://www.redhat.com/en/blog/apis-soap-rest-graphql-grpc)).
- **GraphQL** — best when you must give frontend teams maximum flexibility over what data they fetch, and support varied client shapes ([Red Hat](https://www.redhat.com/en/blog/apis-soap-rest-graphql-grpc)).

> These are not mutually exclusive. A common mature topology: **GraphQL or REST at the public edge / BFG, gRPC between internal services, and async messaging for events** ([file 03](03-microservices.md), [file 04](04-event-driven-cqrs.md)).

---

## 2. REST done properly

REST is more than "JSON over HTTP." The principles that actually matter:
- **Resources & nouns**, not verbs in URLs: `POST /orders`, `GET /orders/42`, not `/createOrder`.
- **HTTP methods carry semantics:** `GET` (safe, idempotent), `PUT`/`DELETE` (idempotent), `POST` (not idempotent), `PATCH` (partial update). Respecting idempotency lets clients and proxies retry safely — directly relevant to the [reliability patterns](04-event-driven-cqrs.md).
- **Status codes mean things:** 2xx success, 4xx client error (400 validation, 401 unauthenticated, 403 unauthorized, 404 not found, 409 conflict, 422 unprocessable), 5xx server error. Don't return 200 with an error body.
- **Statelessness** — each request carries everything needed; no server-side session affinity. This is what lets you scale horizontally ([12-factor](12-scalability-reliability.md)).
- **HATEOAS** — the formal top of the REST maturity model (responses include links to next actions). Rarely fully implemented; know it exists, don't over-invest.
- **Pagination, filtering, sorting** — design these from day one (cursor-based pagination scales better than offset).

---

## 3. Contracts, versioning, and evolution

The hardest part of API design is **changing it without breaking consumers**:
- **Make additive changes, not breaking ones.** Adding an optional field or endpoint is safe; removing/renaming a field or changing its type is breaking.
- **Protobuf/gRPC** enforce this with field numbers and reserved tags — backward compatibility is structural if you follow the rules (never reuse a field number, only add new ones).
- **Versioning strategies:** URL (`/v1/`), header, or media-type. URL versioning is the most pragmatic and visible. Avoid versioning until you must — additive evolution buys you a long time.
- **Contract-first** — define the `.proto`/OpenAPI/GraphQL schema *before* implementation, generate stubs, and use it for **consumer-driven contract testing** ([file 07](07-testing-tdd.md)) so a provider change can't silently break a consumer.

---

## 4. Cross-cutting API concerns

- **Authentication vs authorization** — *who you are* (OAuth2/OIDC, JWT, mTLS) vs *what you may do* (RBAC/ABAC). Validate tokens at the edge *and* enforce authorization in the service.
- **Idempotency keys** — let clients safely retry non-idempotent operations (e.g., payments) by sending a unique key the server dedupes on. Pairs with the [inbox pattern](04-event-driven-cqrs.md).
- **Rate limiting & quotas** — protect against abuse and cascading load; return `429` with `Retry-After`.
- **Pagination & payload limits** — never return unbounded collections.
- **Error format consistency** — adopt a standard (e.g., RFC 9457 *Problem Details for HTTP APIs*) so every error looks the same.
- **Documentation** — OpenAPI/Swagger, gRPC reflection, GraphQL introspection. An undocumented API is an unusable API.
- **Observability** — expose correlation/trace IDs and structured logs at the API boundary ([file 12](12-scalability-reliability.md)).

---

## 5. Design heuristics

- **Design for the consumer, not the database.** The API should express the domain and the client's needs, not leak your table structure.
- **Make illegal states unrepresentable** in the schema where possible (use enums, required fields, value types).
- **Be conservative in what you send, liberal in what you accept** (Postel's Law) — but not so liberal that you accept garbage that bites you later.
- **Fail loudly and early** — validate at the boundary and return precise, actionable errors.

---

## Key sources
- [REST vs GraphQL vs gRPC — Baeldung](https://www.baeldung.com/rest-vs-graphql-vs-grpc).
- [An architect's guide to APIs: SOAP, REST, GraphQL, gRPC — Red Hat](https://www.redhat.com/en/blog/apis-soap-rest-graphql-grpc).
- [REST vs GraphQL vs gRPC design approaches — Alex Xu / ByteByteGo](https://www.linkedin.com/posts/alexxubyte_systemdesign-coding-interviewtips-activity-7459629754078535680-Frpz).
- *RESTful Web APIs* (Richardson & Amundsen); the official [gRPC](https://grpc.io/docs/) and [GraphQL](https://graphql.org/learn/) docs.
