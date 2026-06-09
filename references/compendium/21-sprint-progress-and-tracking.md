# 21 — Sprint Progress & Tracking: Defining "Progress" and Charting It

[File 20](20-sprint-planning-and-scoping.md) covered how a sprint is *defined and scoped*. This file covers what happens once it's running: **how progress is defined, measured, visualized, and forecast** — both within a single sprint and across many.

The central thesis, straight from the Scrum Guide: forecasting practices like burn-downs, burn-ups, and cumulative flows are *proven useful but do not replace empiricism*. In complex work, only **what has already happened** can drive forward-looking decisions ([Scrum Guide 2020 — Sprint](https://scrumguides.org/scrum-guide.html#the-sprint)). Every metric below is a lens on the past used to make a probabilistic bet on the future — never a guarantee.

---

## 1. What counts as "progress"? Define it before you measure it

The most common tracking failure is measuring the wrong thing. Three definitions of progress, in increasing order of honesty:

1. **Activity** ("we wrote a lot of code", "tickets are in progress") — almost worthless. Busyness is not progress.
2. **Output** ("8 of 12 stories closed", "40 of 60 points burned") — useful for in-sprint pacing, but a half-built feature is worth zero.
3. **Outcome** ("guest checkout now works end-to-end; abandonment dropped") — the only definition that matters to stakeholders.

The discipline that makes output trustworthy is the **Definition of Done (DoD)**: an item only contributes to progress when it meets the DoD — tested, reviewed, integrated, releasable ([Scrum Guide 2020 — DoD](https://scrumguides.org/scrum-guide.html#commitment-the-definition-of-done)). This is why **no partial credit** is the standard rule: a story is either Done (counts) or not Done (counts zero), with no "80% done" ([r/agile — velocity counts only completed stories](https://www.reddit.com/r/agile/comments/e2471h/estimating_story_points_vs_pointing_in_time/)). Partial credit is how teams convince themselves they're on track right up until the sprint ends in a pile of 90%-complete work.

> Progress against the **Sprint Goal** is the real measure. A sprint that closes 90% of its points but misses the goal failed; a sprint that drops two low-priority items but nails the goal succeeded. Track the goal first, the numbers second.

---

## 2. The daily feedback loop: the Daily Scrum

In-sprint tracking is not a status report to a manager — it's the team's own steering mechanism. The **Daily Scrum** is a short (≤15 min) developer-owned event to inspect progress toward the Sprint Goal and adapt the plan for the next day ([Scrum Guide 2020 — Daily Scrum](https://scrumguides.org/scrum-guide.html#daily-scrum)). The right framing is **"are we still on track for the goal, and what's blocking us?"** — not "what did you do yesterday" as a surveillance ritual.

The TL's job here is to make **blockers and risk visible immediately**, not at the retrospective when it's too late to act. The chart on the wall (section 3–4) is the artifact the Daily Scrum reads from.

---

## 3. In-sprint tracking: the burndown chart

A **burndown chart** plots **work remaining** (vertical axis) against **time** (horizontal axis, usually days in the sprint). It starts at the total committed work and trends downward as items reach Done — the characteristic downward slope ([SitePoint — Velocity & Burndown](https://www.sitepoint.com/scrum-artifacts-velocity-and-burndown-charts/); [OnlinePMCourses — burndown/burnup/velocity](https://onlinepmcourses.com/what-are-a-burndown-chart-a-burnup-chart-and-velocity/)).

Two lines matter:

- The **ideal line**: a straight diagonal from total work on day 1 to zero on the last day — the constant pace you'd need.
- The **actual line**: the real remaining work, updated daily.

**Reading it (this is the whole point):**

- Actual line **above** ideal → behind pace; the goal is at risk.
- Actual line **flat for several days** → work is started but nothing is *finishing* (too much WIP, or stories too big — see CFD, section 5).
- A **vertical drop** late in the sprint → big stories all completing at once, which means you had no real signal until the end. Slice smaller next time.
- Actual line **dips then rises** → scope was added mid-sprint, or "done" work was reopened.

The value of the burndown is **early detection of deviation** so the team can renegotiate scope while there's still time to protect the goal ([SitePoint](https://www.sitepoint.com/scrum-artifacts-velocity-and-burndown-charts/)).

**Burndown's blind spot:** because it shows a single shrinking number, it **hides scope changes**. If you add as much work as you complete, the line looks healthy while the goalposts move. This is exactly what the burn-up chart fixes.

---

## 4. Burnup chart: making scope changes visible

A **burnup chart** plots **two** lines against time: **total scope** and **work completed** ([Atlassian — Burn up chart](https://www.atlassian.com/agile/project-management/burn-up-chart); [OnlinePMCourses](https://onlinepmcourses.com/what-are-a-burndown-chart-a-burnup-chart-and-velocity/)):

- The **scope line** (total work) — normally flat, but it **steps up when scope is added**, making scope creep impossible to hide.
- The **completed line** — climbs as work finishes.
- The project/sprint is done when the two lines **meet** ([Atlassian](https://www.atlassian.com/agile/project-management/burn-up-chart)).

**Burndown vs. burnup — when to use which:**

| | Burndown | Burnup |
|---|----------|--------|
| Shows | Work remaining | Completed *and* total scope (two lines) |
| Scope changes | **Hidden** | **Visible** (scope line moves) |
| Best for | Quick daily in-sprint pulse | Multi-sprint / release tracking, scope-creep detection |
| Reading | One line vs. ideal | Gap between two lines = work left |

Rule of thumb: **burndown for the sprint's daily heartbeat; burnup the moment scope volatility or a multi-sprint release is in play.**

---

## 5. Cumulative Flow Diagram (CFD): the diagnostic for *flow*

Burn charts tell you *if* you're on pace; the **Cumulative Flow Diagram** tells you *why*. A CFD is a stacked area chart where each colored band is a workflow state (Backlog → In Progress → Review → Done), the horizontal axis is time, and the vertical axis is the cumulative count of work items ([Businessmap — CFD](https://knowledgebase.businessmap.io/hc/en-us/articles/360015034420-The-Cumulative-Flow-Diagram-CFD); [getnave — CFD](https://getnave.com/cumulative-flow-diagram)).

It encodes three flow metrics geometrically ([Hyperdrive — Master the CFD](https://hyperdriveagile.com/downloads/what-is-the-cumulative-flow-diagram-how-to-master-it-34); [Businessmap](https://knowledgebase.businessmap.io/hc/en-us/articles/360015034420-The-Cumulative-Flow-Diagram-CFD)):

- **WIP** = the **vertical** height of the in-progress bands. A band that swells means too much started, not enough finished.
- **Cycle Time** = the **horizontal** distance for an item to cross from "In Progress" to "Done." A widening horizontal gap means work is taking longer to flow through.
- **Throughput** = the **slope of the Done band** — items completed per unit time.

**Diagnostics at a glance:**

- **Parallel, evenly-spaced bands** → stable, healthy flow; arrival rate ≈ completion rate.
- **A widening band** (e.g., "Review" ballooning) → a **bottleneck** at that stage; items arrive faster than they leave ([Businessmap](https://knowledgebase.businessmap.io/hc/en-us/articles/360015034420-The-Cumulative-Flow-Diagram-CFD)).
- **A flattening "Done" slope** → throughput is dropping.
- **The Backlog band growing faster than Done climbs** → you're taking on work faster than you finish it; the line will never converge.

The standard remedy for a bottleneck the CFD reveals is a **WIP limit**: cap how many items can sit in a stage so people *pull* new work only when they finish current work — which raises throughput and shortens cycle time ([Businessmap](https://knowledgebase.businessmap.io/hc/en-us/articles/360015034420-The-Cumulative-Flow-Diagram-CFD)).

---

## 6. Velocity: a planning input, not a scoreboard

**Velocity** is the amount of work (usually story points, sometimes item count) a team completes in a typical sprint, measured historically from sprint to sprint ([SitePoint](https://www.sitepoint.com/scrum-artifacts-velocity-and-burndown-charts/)). Its legitimate use is **forecasting** — "given we average ~40 points/sprint, the remaining 160 points are roughly 4 sprints."

Critical properties teams get wrong:

- It is **measured, not targeted.** A healthy velocity chart trends toward a **horizontal average**, *not* an ever-rising line. "Velocity going up every sprint" is usually point inflation, not improvement ([SitePoint](https://www.sitepoint.com/scrum-artifacts-velocity-and-burndown-charts/)).
- It is **not a productivity or efficiency metric**, and you **cannot compare velocity across teams** — points are relative to each team's own baseline ([Scrum.org — Story Points](https://www.scrum.org/resources/blog/story-points-estimate-or-not-estimate); [OnlinePMCourses](https://onlinepmcourses.com/what-are-a-burndown-chart-a-burnup-chart-and-velocity/)).
- Use a **rolling average** of several recent sprints (commonly the last ~3–8) for stability rather than reacting to any single sprint ([SitePoint](https://www.sitepoint.com/scrum-artifacts-velocity-and-burndown-charts/); [r/agile](https://www.reddit.com/r/agile/comments/e2471h/estimating_story_points_vs_pointing_in_time/)).

> The moment velocity becomes a performance target imposed from above, it gets gamed: estimates inflate, the number rises, and it stops describing reality ([Scrum.org](https://www.scrum.org/resources/blog/story-points-estimate-or-not-estimate)).

---

## 7. Flow metrics: the estimate-free way to track progress

For Kanban-leaning or mature teams, the three **flow-based metrics** track progress without story points at all ([Scrum.org — Story Points: To Estimate or Not](https://www.scrum.org/resources/blog/story-points-estimate-or-not-estimate)):

- **Work in Progress (WIP)** — how many items are in flight right now. Lower, capped WIP → shorter cycle times (Little's Law in practice).
- **Cycle Time** — how long an item takes from "started" to "done." Plotted as a **scatter plot**, it exposes variability and lets you quote percentiles ("85% of items finish in ≤6 days").
- **Throughput** — items completed per unit time. This is the raw material for probabilistic forecasting.

These answer the real planning question — *"how much can be done in a given period, at a given level of risk"* — more honestly than summing points, because they're built from observed reality, not guesses ([Scrum.org](https://www.scrum.org/resources/blog/story-points-estimate-or-not-estimate)).

---

## 8. Forecasting completion: Monte Carlo over a single date

The single biggest upgrade to multi-sprint tracking is replacing "the deadline is March 14" with a **probability distribution**. A **Monte Carlo simulation** feeds historical throughput into thousands of randomized scenarios to produce a *range plus a probability* ([The Burndown — Monte Carlo for Agile](https://theburndown.com/monte-carlo-forecasting-for-agile-teams/); [AgileSeekers — Monte Carlo timelines](https://agileseekers.com/blog/using-monte-carlo-simulations-to-predict-delivery-timelines)).

The three steps ([The Burndown](https://theburndown.com/monte-carlo-forecasting-for-agile-teams/)):

1. Gather historical **actual throughput** data (items completed per sprint/week).
2. Run many simulations sampling randomly from that history.
3. Extract and visualize the result as a **cumulative probability chart** ([AgileSeekers](https://agileseekers.com/blog/using-monte-carlo-simulations-to-predict-delivery-timelines)).

The output is intentionally two-part — **a range and a confidence**: e.g. *"20 stories can be completed in 10 days or less, with 85% probability,"* or *"there's a 50% chance this story finishes in ≤8 days"* ([The Burndown](https://theburndown.com/monte-carlo-forecasting-for-agile-teams/)). This lets a TL/PO communicate deadlines honestly: commit to the date you can hit at 85–90% confidence, not the optimistic 50% one.

**Why it beats point-summing + velocity:** velocity-based forecasts assume a single average and hide variance; Monte Carlo *uses* the variance, so it tells you not just *when* but *how likely*. It also needs only throughput counts, so it works even for teams that don't estimate ([The Burndown](https://theburndown.com/monte-carlo-forecasting-for-agile-teams/)).

---

## 9. The end-of-sprint inspection loops

Tracking culminates in two events that turn data into adaptation:

- **Sprint Review** — inspect the **increment** with stakeholders and adapt the **Product Backlog**. The metric that matters: did we move toward the product goal / sprint goal? It's a working session about *the product*, not a demo theatre ([Scrum Guide 2020 — Sprint Review](https://scrumguides.org/scrum-guide.html#sprint-review)).
- **Sprint Retrospective** — inspect the **process** (people, interactions, tools, Definition of Done) and commit to concrete improvements for the next sprint. This is where the CFD bottlenecks, burndown anomalies, and cycle-time outliers get turned into actions ([Scrum Guide 2020 — Sprint Retrospective](https://scrumguides.org/scrum-guide.html#sprint-retrospective)).

Crucially, the retrospective is where you **calibrate estimation itself** — reviewing where forecasts diverged from reality to improve future sizing ([Atlassian — estimation](https://www.atlassian.com/agile/project-management/estimation)). Tracking that doesn't feed back into planning is just bookkeeping.

---

## 10. Choosing your tracking stack

| Question you need answered | Best tool |
|----------------------------|-----------|
| Are we on pace *today*, within this sprint? | **Burndown** |
| Is scope creeping during a release? | **Burnup** |
| *Why* are we slow — where's the bottleneck? | **Cumulative Flow Diagram** |
| How much can we plan for next sprint? | **Velocity** (rolling avg) or **Throughput** |
| How long do items actually take? | **Cycle Time** (scatter plot, percentiles) |
| When will the release ship, and how sure are we? | **Monte Carlo** forecast (range + probability) |

A practical default for a backend/distributed team: **burndown for the daily pulse, a CFD for diagnosing flow problems, and Monte Carlo over throughput for any external delivery date.** Keep velocity as an internal planning input only — never on a dashboard that management reads as a scoreboard.

---

## Key sources

- [The 2020 Scrum Guide — Sprint, Daily Scrum, Review, Retrospective, Definition of Done](https://scrumguides.org/scrum-guide.html) — empiricism, the events, and the "burn-downs don't replace empiricism" caveat.
- [SitePoint — Scrum Artifacts: Velocity and Burndown Charts](https://www.sitepoint.com/scrum-artifacts-velocity-and-burndown-charts/) — burndown mechanics; velocity as a forecasting tool, not a KPI.
- [Atlassian — Burn up chart](https://www.atlassian.com/agile/project-management/burn-up-chart) — burnup's two lines and scope-creep visibility.
- [OnlinePMCourses — Burndown, Burnup, and Velocity](https://onlinepmcourses.com/what-are-a-burndown-chart-a-burnup-chart-and-velocity/) — clear contrast between the three.
- [Businessmap — The Cumulative Flow Diagram](https://knowledgebase.businessmap.io/hc/en-us/articles/360015034420-The-Cumulative-Flow-Diagram-CFD) and [Hyperdrive — Master the CFD](https://hyperdriveagile.com/downloads/what-is-the-cumulative-flow-diagram-how-to-master-it-34) — WIP, cycle time, throughput, bottleneck reading, WIP limits.
- [Scrum.org — Story Points: To Estimate or Not to Estimate](https://www.scrum.org/resources/blog/story-points-estimate-or-not-estimate) — flow metrics (WIP, cycle time, throughput) and the warning against weaponizing velocity.
- [The Burndown — Monte Carlo Forecasting for Agile Teams](https://theburndown.com/monte-carlo-forecasting-for-agile-teams/) and [AgileSeekers — Monte Carlo timelines](https://agileseekers.com/blog/using-monte-carlo-simulations-to-predict-delivery-timelines) — probabilistic forecasting (range + probability) from historical throughput.
