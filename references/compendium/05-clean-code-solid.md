# 05 — Clean Code & SOLID

Architecture organizes modules; this file is about the quality *inside* a module. Code is read far more often than it is written, and the dominant cost of software is **maintenance**, not initial authoring. Clean code is therefore an economic decision: it lowers the cost of every future change.

---

## 1. Clean Code fundamentals (Robert C. Martin)

- **Meaningful names.** Names should reveal intent. A reader shouldn't need a comment to know what a variable is for. Avoid disinformation, encodings (Hungarian notation), and noise words. `elapsedTimeInDays` beats `d`.
- **Small functions, doing one thing.** A function should do one thing, at one level of abstraction. If you can extract another function with a meaningful name, it was doing more than one thing.
- **Few arguments.** Zero is ideal, three is a smell. Many arguments → introduce a parameter object.
- **No side effects** the name doesn't advertise. A function called `checkPassword` should not also initialize a session.
- **Comments are a failure to express in code.** The best comment is the one you didn't need because the code is clear. Keep comments for *why*, not *what*. Delete commented-out code — version control remembers.
- **Command/Query Separation.** A method either *does* something (command, returns void) or *answers* something (query, returns a value), never both.
- **Error handling is a concern of its own** — prefer exceptions to returned error codes (in languages built for it), don't return or pass `null`, and keep the happy path readable.
- **The Boy Scout Rule:** leave the code cleaner than you found it.

> Clean code is *focused* — each routine, class, and module is dedicated to a single purpose, undistracted by surrounding details.

---

## 2. SOLID — the five OO design principles

SOLID (Robert C. Martin) is a set of principles for writing object-oriented code that is maintainable, extensible, and testable ([DigitalOcean — SOLID](https://www.digitalocean.com/community/conceptual-articles/s-o-l-i-d-the-first-five-principles-of-object-oriented-design); [Wikipedia — SOLID](https://en.wikipedia.org/wiki/SOLID)).

### S — Single Responsibility Principle (SRP)
A class should have only one reason to change — one responsibility ([Wikipedia](https://en.wikipedia.org/wiki/SOLID)). Operationally: ask *"what would cause this class to change?"* If there are multiple independent answers (a change in the report format vs. a change in the tax rules), those are separate responsibilities and belong in separate classes ([DigitalOcean](https://www.digitalocean.com/community/conceptual-articles/s-o-l-i-d-the-first-five-principles-of-object-oriented-design)). A subtler framing: a module should be responsible to **one actor / stakeholder**.

### O — Open/Closed Principle (OCP)
Software entities should be **open for extension but closed for modification** ([Wikipedia](https://en.wikipedia.org/wiki/SOLID)). Add behavior by adding new code (a new class implementing an interface), not by editing existing, tested code ([DigitalOcean](https://www.digitalocean.com/community/conceptual-articles/s-o-l-i-d-the-first-five-principles-of-object-oriented-design)). Achieved via polymorphism/strategy. **Caveat:** don't pre-build extension points everywhere — that's speculative generality. Apply OCP at the axes of change you can actually foresee.

### L — Liskov Substitution Principle (LSP)
Subtypes must be substitutable for their base types without breaking callers ([Splunk — SOLID](https://www.splunk.com/en_us/blog/learn/solid-design-principle.html)). The classic violation is the Rectangle/Square problem: a `Square` that inherits from `Rectangle` breaks code that sets width and height independently. LSP is really about **honoring the base type's contract** (pre/postconditions, invariants), not just matching method signatures.

### I — Interface Segregation Principle (ISP)
Clients should not be forced to depend on methods they don't use. Prefer many small, role-specific interfaces over one fat interface ([Wikipedia](https://en.wikipedia.org/wiki/SOLID)). A fat interface couples unrelated clients: a change for one forces recompilation/rework on all.

### D — Dependency Inversion Principle (DIP)
Depend on **abstractions, not concretions**. High-level policy should not depend on low-level detail; both should depend on abstractions ([Wikipedia](https://en.wikipedia.org/wiki/SOLID)). This is the principle that makes [Clean/Hexagonal architecture](01-architecture-principles.md) possible: the domain defines an interface, infrastructure implements it. Enables loose coupling, easy mocking in tests, and swapping implementations ([Wikipedia](https://en.wikipedia.org/wiki/SOLID)).

---

## 3. The deeper metrics behind SOLID: cohesion & coupling

SOLID is a means to two ends:
- **High cohesion** — elements inside a module belong together and change together.
- **Low coupling** — modules know as little as possible about each other; you can change one without a ripple through the rest.

If a refactor toward SOLID *increases* coupling or scatters a single concept across many files, you've misapplied it. Use the principles in service of these metrics, not as dogma.

---

## 4. Anti-patterns & cautions

- **Anemic Domain Model** — data classes with no behavior, all logic in "service" classes. Sometimes fine (CRUD), but in a rich domain it scatters invariants and defeats OO.
- **God class / God object** — one class that knows and does everything. The SRP violation par excellence.
- **Premature abstraction** — introducing interfaces and indirection "in case we need it." Adds cost now for a benefit that may never come. Prefer the rule of three: extract an abstraction only after you've seen the duplication three times.
- **Over-applying SOLID** — five tiny classes and three interfaces to do what one readable 30-line class did. Clean code is *readable* code; ceremony that hurts readability is not clean.

---

## Key sources
- Robert C. Martin — *Clean Code* and *Clean Coder*.
- [SOLID — Wikipedia](https://en.wikipedia.org/wiki/SOLID) · [DigitalOcean — SOLID Principles](https://www.digitalocean.com/community/conceptual-articles/s-o-l-i-d-the-first-five-principles-of-object-oriented-design) · [Splunk — SOLID with examples](https://www.splunk.com/en_us/blog/learn/solid-design-principle.html).
- Steve McConnell — *Code Complete* (the encyclopedic complement), [file 13](13-reading-list.md).
