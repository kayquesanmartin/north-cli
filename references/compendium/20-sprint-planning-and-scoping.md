# 20 — Sprint Planning & Scoping: How a Tech Lead and PO Define, Slice, and Focus a Sprint

This file is about the *decision-making* that happens before and during Sprint Planning: how a Product Owner (PO) and a Tech Lead (TL) jointly decide **what** a sprint is for, **how much** goes into it, **how it gets sliced**, and **how deadlines are set** without lying to anyone. The companion file ([21 — Sprint Progress & Tracking](21-sprint-progress-and-tracking.md)) covers what happens *after* the sprint starts.

The mental model to hold throughout: a sprint is not a container you fill to the brim — it is a **bet on a single outcome**, time-boxed so that being wrong is cheap and recoverable.

---

## 1. The three questions every Sprint Planning must answer

The 2020 Scrum Guide is explicit that Sprint Planning addresses three topics, in this order — **Why, What, How** ([Scrum Guide 2020 — Sprint Planning](https://scrumguides.org/scrum-guide.html#sprint-planning)). The 2020 edition deliberately added **Why** to the older two-question (What/How) format — making the Sprint Goal a first-class output rather than an afterthought ([Mountain Goat Software — 2020 changes](https://www.mountaingoatsoftware.com/blog/top-5-changes-in-the-2020-version-of-the-scrum-guide)).

| Topic | Owner of the answer | What it produces |
|-------|--------------------|------------------|
| **Why is this sprint valuable?** | PO proposes; whole team commits | The **Sprint Goal** — one coherent objective |
| **What can be done?** | Developers select (with PO) | The selected Product Backlog items |
| **How will it get done?** | Developers (TL facilitates) | The plan / task breakdown |

The Sprint Goal, the selected items, and the plan together are the **Sprint Backlog** ([Scrum Guide 2020](https://scrumguides.org/scrum-guide.html#sprint-backlog)). Planning is time-boxed to a maximum of 8 hours for a one-month sprint, proportionally shorter for shorter sprints ([Scrum Guide 2020](https://scrumguides.org/scrum-guide.html#sprint-planning)).

**The role split that actually works in practice:**

- The **PO owns the Why and the priority order** of the What. They are accountable for maximizing the value of the product and for Product Backlog ordering — but they do **not** dictate how much the team takes on, and they do **not** decide the How.
- The **Developers (with the TL as the senior technical voice) own the How and the size of the commitment.** Only the people doing the work forecast how much fits. Anyone telling developers how to turn items into an increment is overstepping ([Scrum Guide 2020 — Sprint Planning, Topic Three](https://scrumguides.org/scrum-guide.html#sprint-planning)).

> Anti-pattern: the PO (or a manager) decides the sprint scope and hands it to the team as a quota. This converts a *forecast* into a *commitment under duress* and is the single most common cause of quality erosion and burndown theatre.

---

## 2. Defining the Sprint Goal — focusing the result

The Sprint Goal is the **single most important focusing device** the TL and PO have. It is the answer to "if we only achieve one thing this sprint, what is it?" Everything else in the sprint is negotiable in service of the goal.

A strong Sprint Goal is:

- **Outcome-oriented, not output-oriented.** "Reduce checkout abandonment by enabling guest checkout" beats "complete tickets PAY-101 through PAY-109." The goal describes a *change in the world*, the backlog items are merely the bet on how to get there.
- **Singular and coherent.** One theme. If you can't state the goal without using "and," you probably have two sprints' worth of intent competing for focus.
- **A negotiation lever.** When mid-sprint reality bites, the team renegotiates *scope* with the PO while protecting the *goal*. The goal is the thing you defend; individual items are expendable.

**Why the goal precedes the item selection:** selecting items first and writing a goal to fit them afterwards produces an incoherent grab-bag. Propose the value first (PO), let the team pull the items that serve it. This is why the Scrum Guide insists the goal "must be finalized prior to the end of Sprint Planning" ([Scrum Guide 2020](https://scrumguides.org/scrum-guide.html#sprint-planning)).

---

## 3. Readiness: what must be true *before* an item enters a sprint

The **Definition of Ready (DoR)** is the gate that prevents half-understood work from poisoning a sprint. It is not part of core Scrum, but most mature teams use it during refinement and as an entry filter at planning ([Scrum Alliance — DoD vs DoR](https://resources.scrumalliance.org/Article/definition-vs-ready)).

Crucially, the DoR and the DoD point at different things ([Scrum Alliance](https://resources.scrumalliance.org/Article/definition-vs-ready)):

- **DoR** refers to **externalities** — is this item understood, sized, and unblocked enough that the team is confident it can be *finished* within a sprint? (clear acceptance criteria, dependencies identified, design questions resolved, testable).
- **DoD** refers to the **item itself** — what quality bar the increment must meet to be called "Done" and releasable (tested, reviewed, documented, no known regressions) ([Scrum Guide 2020 — Definition of Done](https://scrumguides.org/scrum-guide.html#commitment-the-definition-of-done)).

A practical DoR for a backend-heavy team:

- The user-facing or system outcome is stated (the "why").
- Acceptance criteria exist and are testable.
- External dependencies (other teams, APIs, data, infra) are identified and either resolved or explicitly accepted as risk.
- The item is small enough to plausibly finish in the sprint, or there's a plan to slice it.
- Non-functional expectations (performance, security, observability) are noted where they matter.

> The TL's highest-leverage refinement contribution is killing ambiguity *before* planning. An item that arrives at planning with an unresolved "we'll figure out the data model later" is not ready — it's a research spike wearing a feature's clothes.

---

## 4. Slicing: how to separate work into sprint-sized pieces

The default decomposition heuristic from the Scrum Guide: break Product Backlog items into **work items of one day or less** during the How phase ([Scrum Guide 2020](https://scrumguides.org/scrum-guide.html#sprint-planning)). But the harder, more valuable skill is slicing the *backlog items themselves* so each is independently valuable and finishable.

### Vertical slicing beats horizontal slicing

The cardinal rule: **slice vertically (by user-visible outcome), not horizontally (by technical layer).**

- **Horizontal (avoid):** "Build the database schema" → "Build the API" → "Build the UI." Nothing is shippable until all three land. You can't demo or learn anything until the last slice, and a slip in any layer blocks the outcome.
- **Vertical (prefer):** "A user can submit a guest checkout with one payment method." This cuts through DB + API + UI for one thin path, end-to-end. It's demoable, testable against the goal, and de-risks the whole feature early.

Common slicing patterns: by **workflow step**, by **business rule variation** (happy path first, edge cases later), by **data variation** (one currency, then many), by **interface** (API first, UI next), and by **CRUD operation** (read before write). For a distributed/event-driven system, a useful slice is often *one event flowing end-to-end through the pipeline* before fanning out to all producers/consumers.

### The INVEST checklist for a well-sliced item

A good backlog item is **I**ndependent, **N**egotiable, **V**aluable, **E**stimable, **S**mall, **T**estable. If an item fails one of these, it's a signal to re-slice or refine. "Estimable" failing usually means it's really a spike; "Small" failing means split it; "Valuable" failing means it's a horizontal slice that should be merged into a vertical one.

### Spikes — quarantining the unknown

When an item isn't estimable because of genuine technical uncertainty, separate the *learning* from the *building*: create a time-boxed **spike** whose deliverable is a decision or a thin prototype, not production code. This keeps uncertainty from contaminating the team's ability to forecast the rest of the sprint.

---

## 5. Sizing the commitment: estimation, capacity, and "how much fits"

The Scrum Guide is deliberately silent on *how* to estimate — it only says that the more the developers know about **past performance, upcoming capacity, and their Definition of Done**, the more confident their forecast ([Scrum Guide 2020](https://scrumguides.org/scrum-guide.html#sprint-planning)). Those three inputs are the foundation of every credible sizing method.

### Story points: relative effort, not time

Story points express the **relative** effort, complexity, and risk of an item — not hours ([Atlassian — Story points & estimation](https://www.atlassian.com/agile/project-management/estimation)). The point of using points instead of hours:

- They fold **complexity, risk, and uncertainty** into one number, not just duration ([r/agile discussion](https://www.reddit.com/r/agile/comments/e2471h/estimating_story_points_vs_pointing_in_time/)).
- They reduce the "estimate becomes a promise tattooed on your arm" dynamic that time estimates invite ([r/agile](https://www.reddit.com/r/agile/comments/e2471h/estimating_story_points_vs_pointing_in_time/)).
- Two developers of different speeds give the same point value for the same story, which makes the estimate about the *work*, not the *person*.

The common technique is **planning poker**: discuss the item, everyone reveals an estimate simultaneously, and divergence triggers a short conversation to surface hidden assumptions ([Atlassian](https://www.atlassian.com/agile/project-management/estimation)). Atlassian's practical thresholds: no single item above ~16 hours / ~20 points — beyond that, confidence collapses and you must break it down; for deep-backlog items, give only a rough ballpark because requirements will shift before you start ([Atlassian](https://www.atlassian.com/agile/project-management/estimation)).

> **Hard rule from the field:** points are for *forecasting and conversation*, never for comparing teams or measuring developer productivity. The moment management weaponizes velocity as a performance metric, teams inflate estimates and the number becomes fiction ([Scrum.org — Story Points: To Estimate or Not](https://www.scrum.org/resources/blog/story-points-estimate-or-not-estimate)).

### Capacity-based planning

Velocity (historical points/sprint) tells you a sustainable *average*; capacity adjusts it for *this* sprint's reality:

- Subtract holidays, PTO, on-call rotations, planned meetings, and any commitments to other teams.
- Account for support/interrupt load if the team carries it.
- A common pragmatic approach: take the rolling average velocity of the last ~3 sprints ("**Yesterday's Weather**") as the planning target, then haircut it for known capacity reductions ([r/agile — Yesterday's Weather](https://www.reddit.com/r/agile/comments/e2471h/estimating_story_points_vs_pointing_in_time/)).

### The flow-based / #NoEstimates alternative

Mature teams increasingly skip points and forecast directly from **flow metrics**: Work in Progress, Cycle Time, and Throughput ([Scrum.org](https://www.scrum.org/resources/blog/story-points-estimate-or-not-estimate)). If you know your team historically completes *N* items per sprint and your items are sliced to a consistent small size, "how many fit" becomes "roughly our throughput" — and you forecast longer-range delivery with a **Monte Carlo simulation** over historical throughput instead of summing points (covered in [file 21](21-sprint-progress-and-tracking.md)). Relative sizing beats time-based estimation on variance, and even *no* estimates can beat time-based estimation on predictability for mature teams with small, uniform items ([r/agile](https://www.reddit.com/r/agile/comments/e2471h/estimating_story_points_vs_pointing_in_time/)).

---

## 6. Setting deadlines without lying

This is where the TL earns their seat. Stakeholders want a date; the honest answer is a *range with a confidence level*, not a single day.

### Forecasts, not commitments

A sprint produces a **forecast** of what the team believes it can complete, derived from past performance and capacity ([Scrum Guide 2020](https://scrumguides.org/scrum-guide.html#sprint-planning)). The sprint **timebox** is fixed (e.g., always 2 weeks); the **scope** flexes within it. This is the inversion that makes Agile honest: in waterfall you fix scope and let the date slip; in Scrum you fix the date (the sprint boundary) and let scope flex.

### Communicating release deadlines (multi-sprint)

For a deadline that spans many sprints, never quote a single date. Instead:

1. Forecast a **range** using velocity bands (pessimistic / likely / optimistic) or, better, a **Monte Carlo simulation** over historical throughput, which yields statements like *"85% probability of completing the remaining scope within 6 sprints"* ([The Burndown — Monte Carlo for Agile](https://theburndown.com/monte-carlo-forecasting-for-agile-teams/)).
2. Re-forecast every sprint as real data accrues — the range narrows as you approach delivery.
3. Make the trade-off explicit: a fixed date means scope flexes; fixed scope means the date flexes. You cannot fix both without flexing quality, and flexing quality just moves the cost to later (interest on technical debt).

### The TL's deadline discipline

- **Protect the Definition of Done.** The fastest way to hit a fake deadline is to skip tests, reviews, and observability — and the fastest way to miss the *next* deadline is to have done so. "Done" must mean releasable, every sprint ([Scrum Guide 2020 — DoD](https://scrumguides.org/scrum-guide.html#commitment-the-definition-of-done)).
- **Surface dependencies as risks at planning, not at the deadline.** Cross-team dependencies are the silent killers of forecasts.
- **Keep a small slack buffer.** Planning to 100% of capacity guarantees overflow; the goal is sustainable pace, not maximal utilization.

---

## 7. The TL ↔ PO division of responsibility (cheat sheet)

| Decision | Primary owner | The other's role |
|----------|---------------|------------------|
| Sprint Goal / why it's valuable | PO proposes | TL & team commit, sanity-check feasibility |
| Backlog priority order | PO | TL flags technical dependencies & risk |
| What items enter the sprint | Developers select | PO clarifies value & accepts trade-offs |
| How much fits (the forecast) | Developers / TL | PO must respect it, not override it |
| How the work gets built | Developers / TL | PO stays out of the How |
| Definition of Done | Whole team | TL guards the technical quality bar |
| Slicing items into vertical slices | TL + team in refinement | PO ensures each slice is still valuable |
| Release date communication | PO (externally) | TL supplies the forecast range & confidence |

---

## 8. Anti-patterns to refuse

- **Scope stuffing:** filling the sprint to 100%+ of capacity "to be safe." It guarantees spillover, kills the buffer for the unexpected, and corrupts the next forecast.
- **Velocity as a target/KPI:** the instant velocity becomes a goal rather than a forecasting input, it gets gamed ([Scrum.org](https://www.scrum.org/resources/blog/story-points-estimate-or-not-estimate)).
- **Goal-less sprints:** a list of unrelated tickets with no unifying outcome. Without a goal there's nothing to protect when reality intrudes, so everything gets cut equally and nothing meaningful ships.
- **Horizontal slicing:** layer-by-layer work that delivers no demoable value until the very end and hides integration risk.
- **Mid-sprint goal swaps:** changing the *goal* mid-sprint (vs. renegotiating scope toward it) destroys the focus the timebox exists to create. If the goal is truly invalid, the correct move is to cancel the sprint — a PO-only authority — not to silently mutate it.
- **Estimate-as-promise:** treating a forecast as a contract, then punishing the team for variance. This trains teams to pad estimates until the numbers are meaningless.

---

## Key sources

- [The 2020 Scrum Guide — Sprint Planning, Sprint Goal, Definition of Done](https://scrumguides.org/scrum-guide.html) — the canonical, source-of-truth definitions.
- [Mountain Goat Software — Top 5 changes in the 2020 Scrum Guide](https://www.mountaingoatsoftware.com/blog/top-5-changes-in-the-2020-version-of-the-scrum-guide) — why "Why" was added to planning.
- [Scrum Alliance — Definition of Done vs. Definition of Ready](https://resources.scrumalliance.org/Article/definition-vs-ready) — the DoR/DoD distinction.
- [Atlassian — Story points and estimation](https://www.atlassian.com/agile/project-management/estimation) — planning poker, point thresholds, why points over hours.
- [Scrum.org — Story Points: To Estimate or Not to Estimate](https://www.scrum.org/resources/blog/story-points-estimate-or-not-estimate) — points vs. flow metrics, and the "don't weaponize velocity" warning.
- [The Burndown — Monte Carlo Forecasting for Agile Teams](https://theburndown.com/monte-carlo-forecasting-for-agile-teams/) — probabilistic deadlines from throughput.
