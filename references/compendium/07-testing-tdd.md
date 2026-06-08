# 07 — Testing Discipline & TDD

Tests are not about *finding bugs*; they are about **making change cheap and safe**. A system without a fast, trustworthy test suite calcifies — every change risks regression, so changes slow down, so the design rots. Testing discipline is what keeps refactoring (and therefore [clean code](05-clean-code-solid.md)) economically viable.

---

## 1. Test-Driven Development (TDD)

TDD is a technique that guides development by writing tests *first*, developed by Kent Beck as part of Extreme Programming ([Martin Fowler — TDD](https://www.martinfowler.com/bliki/TestDrivenDevelopment.html)). The loop, **Red → Green → Refactor** ([Fowler](https://www.martinfowler.com/bliki/TestDrivenDevelopment.html)):

1. **Red** — write a test for the next bit of functionality. It fails (you haven't built it yet).
2. **Green** — write the *simplest* code that makes the test pass. Don't gold-plate.
3. **Refactor** — with the test as a safety net, improve the structure of both new and old code.

There's a vital pre-step Fowler emphasizes: **first write a list of the test cases** you'll need, then pick one, run the cycle, and add new cases to the list as they occur to you. Sequencing the tests well — choosing tests that drive you quickly to the important design decisions — is a real skill ([Fowler](https://www.martinfowler.com/bliki/TestDrivenDevelopment.html)).

**Why the refactor step is the point.** Beck and Fowler took refactoring as essential to keep the cost of future features low — but refactoring *without* test coverage is just "adding bugs." TDD builds the network of tests that gives you the confidence to refactor aggressively ([r/ExperiencedDevs on TDD](https://www.reddit.com/r/ExperiencedDevs/comments/wrplvh/whats_your_take_on_the_tdd_approach_how_are_tests/)).

**What TDD really gives you:** not just coverage, but *testable design*. Code written test-first tends to have smaller units, fewer hidden dependencies, and clear seams (because untestable code is painful to write tests for first). It's a design feedback loop disguised as a testing practice.

**Honest limits:** TDD shines for logic with clear inputs/outputs and for bug fixes (write a failing test that reproduces the bug first). It's awkward for exploratory/spike work, UI layout, and code whose design you're still discovering. Many seniors do "test-soon" rather than dogmatic test-first, and reserve strict TDD for complex domain logic.

---

## 2. The Test Pyramid

A heuristic for the *shape* of a healthy suite (Mike Cohn, popularized by Fowler):

```
        /\        End-to-End (few)      slow, brittle, high confidence
       /  \
      /    \      Integration (some)    real DB/broker, moderate speed
     /______\
    /        \    Unit (many)           fast, isolated, cheap
   /__________\
```

- **Unit tests** — the broad base. Fast (milliseconds), isolated, test one unit of behavior. You should have thousands and run them on every save.
- **Integration tests** — verify that units work together with real collaborators (a real database, a real broker via Testcontainers). Slower, fewer.
- **End-to-end tests** — exercise the whole system through its public surface. Highest confidence, but slow and flaky. Keep them few and reserve them for critical user journeys.

**Anti-pattern — the "ice-cream cone":** mostly E2E tests, few unit tests. It looks thorough but is slow, flaky, and gives feedback too late. Invert it.

---

## 3. Test doubles (Meszaros' taxonomy)

You isolate a unit by replacing its collaborators with **doubles**:
- **Dummy** — passed but never used (fills a parameter).
- **Stub** — returns canned answers to calls made during the test.
- **Spy** — a stub that also records how it was called.
- **Mock** — pre-programmed with expectations; *verifies* interactions.
- **Fake** — a working but simplified implementation (an in-memory repository).

**Senior caution — don't over-mock.** Mocking everything produces tests coupled to implementation details: they pass while the system is broken and break on harmless refactors. Prefer testing through real or fake collaborators where feasible; mock at true architectural boundaries (the network, the clock, third-party services), not at every internal seam. This is the "London vs. Detroit/Classicist" school debate — lean classicist for domain logic.

---

## 4. Beyond example-based unit tests

- **BDD (Behavior-Driven Development)** — frames tests as behavior specs in business language (Given/When/Then, Gherkin). Improves collaboration with non-engineers and doubles as living documentation. It's TDD with a vocabulary shift toward *behavior* and stakeholders.
- **Contract testing** (e.g., Pact) — for microservices, verify that a consumer and provider agree on the API contract *without* spinning up both. The antidote to brittle cross-service E2E tests. Pairs with [API design](11-api-design.md).
- **Property-based testing** (QuickCheck, Hypothesis, FsCheck) — instead of hand-picked examples, assert *properties* that must hold for all inputs, and let the framework generate (and shrink) counterexamples. Devastatingly effective at finding edge cases.
- **Mutation testing** — deliberately introduce bugs ("mutants") and check that tests catch them; measures the *quality* of your tests, not just coverage.
- **Approval/snapshot tests** — capture output and diff against an approved baseline; great for serialization and rendering.

---

## 5. What makes a good test (FIRST + more)

- **Fast** — or you won't run it.
- **Isolated/Independent** — no order dependence, no shared mutable state.
- **Repeatable** — deterministic; no reliance on wall clock, network, or random seeds (inject them).
- **Self-validating** — pass/fail with no human inspection.
- **Timely** — written close to (or before) the code.
- Plus: **test behavior, not implementation**; one logical assertion per test; arrange-act-assert structure; and a name that states the scenario and expected result.

**Coverage ≠ quality.** 100% line coverage with no meaningful assertions tests nothing. Use coverage to find *untested* code, never as a target to game.

---

## Key sources
- Martin Fowler — [Test-Driven Development](https://www.martinfowler.com/bliki/TestDrivenDevelopment.html) and [TestPyramid](https://martinfowler.com/bliki/TestPyramid.html).
- Kent Beck — *Test-Driven Development by Example*.
- [TDD: Red-Green-Refactor discussion — r/ExperiencedDevs](https://www.reddit.com/r/ExperiencedDevs/comments/wrplvh/whats_your_take_on_the_tdd_approach_how_are_tests/).
- Freeman & Pryce — *Growing Object-Oriented Software, Guided by Tests*; see [file 13](13-reading-list.md).
