# 06 — Design Patterns

Design patterns are **named, proven solutions to recurring design problems** — and just as importantly, a shared vocabulary. Saying "use a Strategy here" communicates a whole structure in two words. The canonical catalog is the 23 patterns from the 1994 *Design Patterns: Elements of Reusable Object-Oriented Software* by Gamma, Helm, Johnson, and Vlissides — the "Gang of Four" (GoF) ([Wikipedia — Design Patterns](https://en.wikipedia.org/wiki/Design_Patterns); [DigitalOcean — GoF patterns](https://www.digitalocean.com/community/tutorials/gangs-of-four-gof-design-patterns)).

The GoF split into three families ([GeeksforGeeks — GoF patterns](https://www.geeksforgeeks.org/system-design/gang-of-four-gof-design-patterns/)):

---

## 1. Creational — *how objects are created*

| Pattern | Intent |
|---|---|
| **Factory Method** | Defer instantiation to subclasses; create objects without naming the concrete class. |
| **Abstract Factory** | Create families of related objects without specifying concrete classes. |
| **Builder** | Separate construction of a complex object from its representation; ideal for objects with many optional parameters ([DigitalOcean](https://www.digitalocean.com/community/tutorials/gangs-of-four-gof-design-patterns)). |
| **Prototype** | Create new objects by cloning an existing instance instead of building from scratch ([DigitalOcean](https://www.digitalocean.com/community/tutorials/gangs-of-four-gof-design-patterns)). |
| **Singleton** | Ensure one instance with a global access point. **Most-abused pattern** — usually a global variable in disguise; it hides dependencies and wrecks testability. Prefer dependency injection. |

---

## 2. Structural — *how objects/classes are composed*

| Pattern | Intent ([DigitalOcean](https://www.digitalocean.com/community/tutorials/gangs-of-four-gof-design-patterns)) |
|---|---|
| **Adapter** | Make two incompatible interfaces work together by wrapping one. (The basis of the Anti-Corruption Layer — [file 02](02-domain-driven-design.md).) |
| **Bridge** | Decouple an abstraction from its implementation so both can vary independently. |
| **Composite** | Compose objects into tree structures; treat individual objects and compositions uniformly. |
| **Decorator** | Attach responsibilities to an object dynamically — a flexible alternative to subclassing. |
| **Facade** | Provide a simplified high-level interface to a complex subsystem. |
| **Flyweight** | Share fine-grained objects to minimize memory (e.g., glyphs in a text editor). |
| **Proxy** | A surrogate controlling access to another object — for lazy loading, remote access, security, logging. |

---

## 3. Behavioral — *how objects interact & distribute responsibility*

| Pattern | Intent ([DigitalOcean](https://www.digitalocean.com/community/tutorials/gangs-of-four-gof-design-patterns)) |
|---|---|
| **Strategy** | A family of interchangeable algorithms; let the algorithm vary independently of clients. The cleanest realization of OCP. |
| **Observer** | One-to-many dependency: when one object changes, dependents are notified. Foundation of event-driven UIs and pub/sub. |
| **Command** | Encapsulate a request as an object — enables queuing, logging, and undo. |
| **State** | Let an object change its behavior when its internal state changes. |
| **Template Method** | Define an algorithm's skeleton, defer steps to subclasses. |
| **Chain of Responsibility** | Pass a request along a chain until someone handles it. (Middleware pipelines.) |
| **Mediator** | Centralize complex communication between objects to reduce direct coupling. |
| **Iterator** | Access elements of a collection sequentially without exposing its structure. |
| **Visitor** | Add a new operation over an object structure without changing its classes. |
| **Memento** | Capture and restore an object's state without violating encapsulation (undo). |
| **Interpreter** | Define a grammar and an interpreter for a small language. |

---

## 4. How a senior actually uses patterns

1. **Recognize, don't impose.** Patterns should *emerge* from refactoring toward a problem, not be chosen up front and forced onto the design. Most overengineering comes from "pattern-driven development."
2. **The vocabulary is half the value.** Even when you don't formally implement them, naming the structure ("this is basically an Observer") accelerates communication and code review.
3. **Many GoF patterns compensate for language limitations.** In languages with first-class functions, the **Strategy** and **Command** patterns often collapse into passing a function/lambda. The Iterator is built into the language. Don't ceremonially recreate what your language gives you for free.
4. **Know the costs.** Every pattern adds indirection. Indirection aids flexibility but harms *traceability* — more files to open to follow one call. Add it when flexibility is needed, not preemptively.

---

## 5. Beyond GoF

The GoF catalog is OO-class-level. Two other tiers matter for system-builders:
- **Enterprise Integration Patterns** (Hohpe & Woolf) — messaging patterns (message channel, router, translator, aggregator) directly relevant to your NATS/RabbitMQ work; see [file 04](04-event-driven-cqrs.md).
- **Patterns of Enterprise Application Architecture** (Fowler) — Repository, Unit of Work, Data Mapper, Domain Model, Service Layer — the patterns behind every ORM and [Clean Architecture](01-architecture-principles.md) implementation. See [file 13](13-reading-list.md).

---

## Key sources
- Gamma, Helm, Johnson, Vlissides — *Design Patterns: Elements of Reusable Object-Oriented Software* ([Wikipedia overview](https://en.wikipedia.org/wiki/Design_Patterns)).
- [GoF Design Patterns — DigitalOcean](https://www.digitalocean.com/community/tutorials/gangs-of-four-gof-design-patterns) · [GeeksforGeeks](https://www.geeksforgeeks.org/system-design/gang-of-four-gof-design-patterns/).
- Refactoring Guru (free, excellent diagrams) and the books in [file 13](13-reading-list.md).
