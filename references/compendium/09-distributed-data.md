# 09 — Distributed Data & Consistency

The moment your data lives on more than one machine, a new class of problems appears that does not exist in a single-box system: networks drop and delay messages, clocks disagree, and nodes fail independently. This file covers the theory and mechanisms for reasoning about correctness when one logical database becomes many physical ones. This is the deep end — and the area where the most expensive production incidents originate.

---

## 1. The CAP theorem

A distributed system can guarantee at most **two** of: **Consistency**, **Availability**, **Partition tolerance** ([Wikipedia — CAP theorem](https://en.wikipedia.org/wiki/CAP_theorem); [Stack Overflow — CAP explained](https://stackoverflow.com/questions/12346326/cap-theorem-availability-and-partition-tolerance)):

- **Consistency** — every read sees the most recent write (here, "linearizability"), so all nodes agree.
- **Availability** — every request gets a (non-error) response, even if a node is down.
- **Partition tolerance** — the system keeps working despite arbitrary message loss/delay between nodes ([Wikipedia](https://en.wikipedia.org/wiki/CAP_theorem)).

**The real interpretation:** networks *will* partition, so partition tolerance is non-negotiable for any real distributed system. CAP therefore reduces to a choice you make **only during a partition** ([Wikipedia](https://en.wikipedia.org/wiki/CAP_theorem)):
- **CP** — refuse/timeout requests that can't be guaranteed current → preserve consistency, sacrifice availability.
- **AP** — answer with possibly-stale data → preserve availability, sacrifice consistency.

When there's *no* partition, you can have both C and A ([Wikipedia](https://en.wikipedia.org/wiki/CAP_theorem)). The popular "pick two" framing is a simplification — the choice is really C-vs-A *during partitions* ([Stack Overflow](https://stackoverflow.com/questions/12346326/cap-theorem-availability-and-partition-tolerance)).

### PACELC — the better model
CAP ignores the normal (non-partitioned) case. **PACELC** extends it: *if Partition (P), trade Availability (A) vs Consistency (C); Else (E), trade Latency (L) vs Consistency (C)* ([Wikipedia](https://en.wikipedia.org/wiki/CAP_theorem)). This captures the everyday reality that even with no failures, stronger consistency costs latency. It's the more useful lens for system design.

---

## 2. Consistency models (a spectrum, not a binary)

Kleppmann's clarification of these terms is one of DDIA's most valuable contributions ([DDIA summary](https://newsletter.techworld-with-milan.com/p/what-i-learned-from-the-book-designing)):

- **Linearizability** (strong) — the system behaves as if there's a single copy of the data and operations happen atomically in real-time order. Easiest to reason about, most expensive.
- **Serializability** — transactions appear to execute in *some* serial order (a transaction-isolation property; see [file 08](08-databases.md)). Distinct from linearizability (a recency/ordering property on single objects).
- **Causal consistency** — operations that are causally related are seen in order by everyone; concurrent ops may be seen in different orders. A strong, achievable middle ground.
- **Eventual consistency** — given no new writes, replicas eventually converge. Cheap and highly available, but reads may be stale and you must design the application to tolerate it.

> **Senior reality:** "eventual consistency" is not a hand-wave — it's a contract you must surface to the product. *How* eventual? Seconds? Can a user read their own write? Design explicit affordances (read-your-writes, monotonic reads) rather than hoping users won't notice.

---

## 3. Replication

Copying data to multiple nodes for availability, read scaling, and locality:
- **Single-leader (primary/replica)** — all writes go to the leader, which streams a replication log to followers. Simple, the default in most relational setups. Risk: **replication lag** (followers serve stale reads) and failover complexity.
- **Multi-leader** — multiple nodes accept writes (e.g., multi-datacenter). Improves write availability/locality but introduces **write conflicts** needing resolution (last-write-wins is lossy; CRDTs or app-level merges are better).
- **Leaderless (Dynamo-style)** — any replica accepts reads/writes; use **quorums** (W + R > N) to bound staleness. Powers Cassandra, DynamoDB.

Key concepts to internalize: **replication lag**, **read-your-writes / monotonic-reads guarantees**, and **synchronous vs asynchronous** replication (durability vs latency trade-off).

---

## 4. Partitioning (sharding)

Splitting data across nodes so each holds a subset, for scale beyond one machine:
- **By key range** — efficient range scans, but risk of hot spots (e.g., time-ordered keys all hitting one shard).
- **By hash of key** — even distribution, but range queries become scatter-gather.
- **Rebalancing** — moving partitions as nodes join/leave without downtime; consistent hashing minimizes movement.
- **Secondary indexes** in a partitioned store are hard — local (per-partition, scatter-gather reads) vs global (term-partitioned, scatter-gather writes).
- The combination of **partitioning + replication** is how every large-scale store (Kafka, Cassandra, Elasticsearch) actually works.

---

## 5. Distributed transactions & consensus

When you genuinely need atomicity across nodes:
- **Two-Phase Commit (2PC)** — a coordinator runs prepare → commit across participants. Provides atomic commit but is a **blocking** protocol: if the coordinator dies after prepare, participants are stuck holding locks. Hurts availability ([DDIA — Distributed Transactions & Consensus chapter](https://0-lucas.github.io/digital-garden/99.-Books/Martin-Kleppmann---Designing-Data-Intensive-Applications_-O%E2%80%99Reilly-Media-(2017).pdf)).
- **Consensus algorithms (Paxos, Raft)** — let a set of nodes agree on a value despite failures; the basis of leader election, distributed locks, and config stores (etcd, ZooKeeper, Consul). Raft is the one to study first — it was explicitly designed to be understandable.
- **Total order broadcast** — delivering messages to all nodes in the same order; equivalent in power to consensus, and the conceptual core of replicated logs like Kafka ([DDIA](https://0-lucas.github.io/digital-garden/99.-Books/Martin-Kleppmann---Designing-Data-Intensive-Applications_-O%E2%80%99Reilly-Media-(2017).pdf)).

**In microservices, prefer sagas over distributed transactions.** 2PC across services couples their availability and is operationally fragile; sagas + eventual consistency + idempotency ([file 03](03-microservices.md), [file 04](04-event-driven-cqrs.md)) is the pragmatic norm.

---

## 6. Faults you must design for

- **Partial failure** — the defining feature of distributed systems: some nodes work, others don't, and you can't always tell which.
- **Unreliable clocks** — wall clocks drift and jump; never use timestamps for ordering correctness. Use logical clocks (Lamport timestamps, vector clocks) when you need causal order.
- **Byzantine faults** — nodes that lie or corrupt data (vs. simply crashing). Tolerating them (BFT algorithms) is costly and complex; most internal systems assume non-Byzantine (crash-stop) faults, which is reasonable inside a trusted datacenter ([DDIA summary](https://newsletter.techworld-with-milan.com/p/what-i-learned-from-the-book-designing)).

---

## Key sources
- Martin Kleppmann — *Designing Data-Intensive Applications*, Part II (the definitive treatment) ([PDF](https://0-lucas.github.io/digital-garden/99.-Books/Martin-Kleppmann---Designing-Data-Intensive-Applications_-O%E2%80%99Reilly-Media-(2017).pdf); [summary](https://newsletter.techworld-with-milan.com/p/what-i-learned-from-the-book-designing)).
- [CAP theorem — Wikipedia](https://en.wikipedia.org/wiki/CAP_theorem) · [CAP explained — Stack Overflow](https://stackoverflow.com/questions/12346326/cap-theorem-availability-and-partition-tolerance).
- The Raft paper, *In Search of an Understandable Consensus Algorithm* (Ongaro & Ousterhout).
