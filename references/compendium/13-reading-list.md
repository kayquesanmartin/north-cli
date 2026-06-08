# 13 — Curated Reading List

The compendium is the map; these are the territory. Ranked and grouped so you can pick a path rather than drown. A **must-read** marker (⭐) flags a book I'd consider non-negotiable for a backend/distributed-systems engineer.

---

## Tier 1 — The foundational canon (read these first)

1. ⭐ **Designing Data-Intensive Applications** — Martin Kleppmann (O'Reilly, 2017). The single best book for backend/distributed engineers. Covers data models, storage engines, replication, partitioning, transactions, consistency, consensus, batch & stream processing — with rigor and honesty about trade-offs ([summary](https://newsletter.techworld-with-milan.com/p/what-i-learned-from-the-book-designing) · [PDF mirror](https://0-lucas.github.io/digital-garden/99.-Books/Martin-Kleppmann---Designing-Data-Intensive-Applications_-O%E2%80%99Reilly-Media-(2017).pdf)). Directly underpins files 04, 08, 09, 12.
2. ⭐ **Clean Code** — Robert C. Martin (Prentice Hall, 2008). Naming, functions, error handling, the day-to-day craft. Opinionated; take the principles, not every rule as gospel. Underpins file 05.
3. **The Pragmatic Programmer** — Hunt & Thomas (20th Anniversary ed., 2019). The mindset book — DRY, orthogonality, tracer bullets, "don't live with broken windows." Broad and timeless.
4. **Code Complete (2nd ed.)** — Steve McConnell (2004). The encyclopedic, evidence-based reference on construction. Complements Clean Code with breadth.

---

## Tier 2 — Architecture & design

5. ⭐ **Clean Architecture** — Robert C. Martin (2017). The Dependency Rule, component principles, boundaries. The book behind file 01 ([blog precursor](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)).
6. ⭐ **Domain-Driven Design** — Eric Evans (2003, the "Blue Book"). The strategic-design source. Dense; pair with the next two. Files 02.
7. **Implementing Domain-Driven Design** — Vaughn Vernon (2013, the "Red Book"). More practical and code-forward than Evans ([sample PDF](https://ptgmedia.pearsoncmg.com/images/9780321834577/samplepages/0321834577.pdf)).
8. **Learning Domain-Driven Design** — Vlad Khononov (O'Reilly, 2021). The gentlest, most modern on-ramp to DDD; start here if Evans is intimidating.
9. ⭐ **Design Patterns** — Gamma, Helm, Johnson, Vlissides (1994, "GoF"). The 23-pattern catalog and shared vocabulary. Reference, not cover-to-cover ([overview](https://en.wikipedia.org/wiki/Design_Patterns)). File 06. (Use [Refactoring Guru](https://refactoring.guru) for friendlier diagrams.)
10. **Patterns of Enterprise Application Architecture** — Martin Fowler (2002). Repository, Unit of Work, Data Mapper, Service Layer — the patterns behind every ORM and layered app. File 06.
11. **Fundamentals of Software Architecture** — Mark Richards & Neal Ford (O'Reilly, 2020). Modern survey of architecture styles, characteristics, and the architect role.
12. **Building Evolutionary Architectures** — Ford, Parsons, Kua (2nd ed.). Fitness functions — encoding architectural rules as automated tests. File 01.

---

## Tier 3 — Distributed systems & microservices

13. ⭐ **Building Microservices (2nd ed.)** — Sam Newman (O'Reilly, 2021). The best end-to-end treatment of decomposition, integration, deployment, and the organizational side. File 03.
14. **Microservices Patterns** — Chris Richardson (Manning, 2018). The pattern catalog (sagas, API composition, CQRS) in book form; companion to [microservices.io](https://microservices.io/patterns/). Files 03–04.
15. **Enterprise Integration Patterns** — Hohpe & Woolf (2003). The messaging bible — channels, routers, translators, aggregators. Essential for your NATS/RabbitMQ work. File 04.
16. **Release It! (2nd ed.)** — Michael Nygard (2018). Stability and resilience patterns (circuit breaker, bulkhead) from hard production experience. Files 03, 12. (Nygard also created the [ADR](14-spec-driven-development.md) format.)

---

## Tier 4 — Process, testing & craft

17. ⭐ **Refactoring (2nd ed.)** — Martin Fowler (2018). The catalog of behavior-preserving transformations and the code smells that trigger them ([book page](https://martinfowler.com/books/refactoring.html) · [catalog](https://refactoring.com/catalog/)). File 07.
18. **Test-Driven Development by Example** — Kent Beck (2002). TDD from its originator, by worked example ([Fowler on TDD](https://www.martinfowler.com/bliki/TestDrivenDevelopment.html)). File 07.
19. **Growing Object-Oriented Software, Guided by Tests** — Freeman & Pryce (2009). The "London school" of TDD; how tests drive design. File 07.
20. **Working Effectively with Legacy Code** — Michael Feathers (2004). How to get untested code under test and change it safely. The book for the real world.
21. **Accelerate** — Forsgren, Humble, Kim (2018). The research linking the four DORA metrics to performance. The evidence base for file 10.
22. **The Phoenix Project** — Kim, Behr, Spafford (2013). DevOps as a novel; the "why" of flow and feedback.

---

## Tier 5 — Operations, reliability & security

23. ⭐ **Site Reliability Engineering** — Google (O'Reilly, 2016, [free online](https://sre.google/books/)). SLI/SLO/SLA, error budgets, toil, postmortems. File 12.
24. **The Site Reliability Workbook** — Google (2018, free online). The practical companion to the above.
25. **Web Application Security** — Andrew Hoffman (O'Reilly, 2020). A developer-focused tour aligned with the [OWASP Top 10](https://owasp.org/www-project-top-ten/). File 12 & 18.

---

## Living references (free, online, keep bookmarked)

- [microservices.io](https://microservices.io/patterns/) — Chris Richardson's pattern language.
- [martinfowler.com](https://martinfowler.com) — bliki entries on virtually every topic here.
- [Azure Architecture Center — Cloud Design Patterns](https://learn.microsoft.com/en-us/azure/architecture/patterns/) — vendor-neutral enough to be broadly useful (files 04, 12).
- [The Twelve-Factor App](https://12factor.net) — file 12.
- [C4 model](https://c4model.com) — Simon Brown's diagramming approach (file 16).
- [GitHub Spec Kit](https://github.com/github/spec-kit) & [Kiro docs](https://kiro.dev/docs/specs/) — Spec-Driven Development (file 14).
- [Refactoring Guru](https://refactoring.guru) — patterns & refactoring with great visuals.
- [OWASP](https://owasp.org/www-project-top-ten/) — security (file 18).

---

## Suggested reading order for your profile (backend / distributed / .NET & Node)

1. **Designing Data-Intensive Applications** (your center of gravity).
2. **Clean Architecture** + **Learning Domain-Driven Design** (shape the system).
3. **Building Microservices** + **Enterprise Integration Patterns** (your distribution & messaging world).
4. **Refactoring** + **Test-Driven Development by Example** (keep it changeable).
5. **Release It!** + **Site Reliability Engineering** (keep it alive in production).
