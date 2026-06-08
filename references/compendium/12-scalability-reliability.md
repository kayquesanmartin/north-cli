# 12 — Scalability, Reliability & Operations

A system is not "done" when it passes tests — it's done when it stays fast, available, and secure under real load, and when you can operate it without heroics. This file covers the operational concerns that separate a demo from a production system: deployability, scaling, caching, observability, reliability engineering, and security baseline.

---

## 1. The Twelve-Factor App — the deployability baseline

The canonical methodology for building software-as-a-service apps that are portable, scalable, and operable ([12factor.net](https://12factor.net); [Wikipedia — Twelve-Factor](https://en.wikipedia.org/wiki/Twelve-Factor_App_methodology)). The twelve factors ([Wikipedia](https://en.wikipedia.org/wiki/Twelve-Factor_App_methodology)):

1. **Codebase** — one codebase tracked in version control, many deploys.
2. **Dependencies** — explicitly declare and isolate; never rely on implicit system packages.
3. **Config** — store config (credentials, hostnames) in the environment, not in code ([externalized configuration](03-microservices.md)).
4. **Backing services** — treat databases, queues, caches as attached, swappable resources.
5. **Build, release, run** — strictly separate these stages.
6. **Processes** — run as one or more **stateless** processes; persist state in backing services. This is what makes horizontal scaling possible.
7. **Port binding** — export services via a port; be self-contained.
8. **Concurrency** — scale out by running more processes (the process model), not just bigger machines.
9. **Disposability** — fast startup and graceful shutdown → robust, elastic systems.
10. **Dev/prod parity** — keep environments as similar as possible to avoid "works on my machine" ([DreamFactory — 12-factor](https://www.dreamfactory.com/resources/whitepapers/implementing-the-twelve-factor-app-methodology)).
11. **Logs** — treat logs as event streams; write to stdout and let the platform aggregate.
12. **Admin processes** — run one-off tasks (migrations) as separate processes against the same release.

> Why it matters for you: factors 6, 8, and 9 (statelessness, process-based concurrency, disposability) are the *preconditions* for autoscaling and zero-downtime deploys in Kubernetes/containers. A stateful, slow-booting process can't be scaled or rescheduled freely.

---

## 2. Scalability

- **Vertical scaling (scale up)** — bigger machine. Simple, but has a ceiling and a single point of failure.
- **Horizontal scaling (scale out)** — more machines behind a load balancer. Effectively unbounded, but *requires statelessness* and introduces distribution problems ([file 09](09-distributed-data.md)).
- **Describe load before discussing growth** — Kleppmann's point: pick **load parameters** (requests/sec, read/write ratio, fan-out, payload size) and reason about what happens when they double ([DDIA summary](https://newsletter.techworld-with-milan.com/p/what-i-learned-from-the-book-designing)).
- **Measure with percentiles, not averages.** p50 hides the pain; p99/p99.9 latency is what your worst-served (often most valuable) users feel. Averages lie when distributions are skewed.
- **Common scaling levers:** stateless app tier + load balancing, read replicas, caching, partitioning/sharding, async processing via queues, CDN for static/edge content.
- **Back-pressure** — when a downstream can't keep up, propagate the slowdown (bounded queues, rejecting load) rather than building unbounded buffers that eventually OOM.

---

## 3. Caching — the double-edged sword

- **Cache layers:** client → CDN → API/gateway → application (in-memory/Redis) → database (buffer pool).
- **Strategies:** cache-aside (lazy), read-through, write-through, write-behind.
- **The hard part is invalidation** — "There are only two hard things in computer science: cache invalidation and naming things." Stale caches cause subtle correctness bugs.
- **Watch for:** thundering herd / cache stampede (many misses hit the DB at once — use locks or request coalescing), and hot keys.

---

## 4. Reliability & SRE

- **Reliability** = continuing to work *correctly* even when things go wrong (hardware, software, and human faults) ([DDIA summary](https://newsletter.techworld-with-milan.com/p/what-i-learned-from-the-book-designing)). Build **fault-tolerant** systems that expect and contain failure rather than chasing fault-*free* components.
- **Redundancy & no single points of failure** — replicate across instances, zones, regions per your availability NFR ([file 10](10-requirements-process.md)).
- **Graceful degradation** — shed non-critical features under stress rather than failing wholesale (e.g., serve cached/stale data, disable recommendations).
- **SRE concepts (Google):**
  - **SLI** (a measured indicator, e.g., success rate), **SLO** (the target, e.g., 99.9%), **SLA** (the contractual promise with consequences).
  - **Error budget** — the allowed unreliability (100% − SLO). Spend it on shipping features; when it's exhausted, freeze risky changes. Aligns dev velocity with reliability.
  - **Toil reduction** — automate repetitive operational work.
  - **Blameless postmortems** — learn from incidents by fixing systems, not punishing people.

---

## 5. Observability — you can't operate what you can't see

The three pillars, plus the modern fourth:
- **Logs** — structured (JSON), with correlation/trace IDs; event streams, not files ([12-factor](https://12factor.net)).
- **Metrics** — numeric time series (rates, errors, durations — the "RED" method; or USE for resources). Cheap, aggregatable, the backbone of alerting and dashboards.
- **Traces** — distributed tracing follows one request across services via a propagated trace ID ([file 03](03-microservices.md)). Essential in microservices.
- **(Profiles/events)** — continuous profiling for the hard performance problems.
- **OpenTelemetry** is the vendor-neutral standard worth standardizing on.
- **Alert on symptoms, not causes** — page on "users see errors / latency is high," not on every CPU spike. Alert fatigue kills on-call.

---

## 6. Security baseline (every developer's responsibility)

Security is not a separate team's job bolted on at the end. Minimum literacy:
- **OWASP Top 10** — know the common web vulnerabilities (injection, broken access control, SSRF, etc.) and their mitigations.
- **Validate all input, encode all output** — injection (SQL, command, XSS) comes from trusting input. Use parameterized queries, never string-concatenate SQL.
- **AuthN vs AuthZ** done right ([file 11](11-api-design.md)); least privilege everywhere.
- **Secrets management** — never in code or images; use a vault/secret manager, rotate regularly ([12-factor config](https://12factor.net)).
- **Encryption** in transit (TLS) and at rest; hash passwords with a slow algorithm (bcrypt/argon2), never reversible encryption.
- **Defense in depth** and **secure defaults** — assume any single control can fail.
- **Supply chain** — pin and scan dependencies (SCA); a vulnerability in a transitive package is your vulnerability.

---

## Key sources
- [The Twelve-Factor App](https://12factor.net) · [Twelve-Factor — Wikipedia](https://en.wikipedia.org/wiki/Twelve-Factor_App_methodology) · [DreamFactory whitepaper](https://www.dreamfactory.com/resources/whitepapers/implementing-the-twelve-factor-app-methodology).
- Martin Kleppmann — *Designing Data-Intensive Applications* (reliability/scalability/maintainability) ([summary](https://newsletter.techworld-with-milan.com/p/what-i-learned-from-the-book-designing)).
- Google — *Site Reliability Engineering* (free online) and the [OWASP Top 10](https://owasp.org/www-project-top-ten/); see [file 13](13-reading-list.md).
