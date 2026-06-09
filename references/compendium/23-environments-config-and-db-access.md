# 23 — Environments, Configuration & Database Access

This file answers a cluster of intensely practical questions every team faces: **how do you organize DEV / TEST / STAGING (HML) / PROD environments? where do configuration and secrets live? how should an application connect to a SQL server in each environment — securely?** It is intentionally stack-agnostic: the principles below apply whether you're on .NET, Node, Java, or Go, and whether you're on AWS, Azure, GCP, or on-prem.

The single organizing principle, from which almost everything else follows: **strict separation of config from code** ([The Twelve-Factor App — Config](https://12factor.net/config)). The same build artifact must run unchanged in every environment; only the injected configuration differs.

---

## 1. The environment ladder: DEV → TEST → HML → PROD

Software is promoted through a sequence of environments, each closer to production. Naming varies by org (and "HML" — *homologação* — is the common Brazilian/Portuguese term for **staging/UAT**), but the ladder is consistent:

| Environment | Also called | Purpose | Who uses it | Data |
|-------------|-------------|---------|-------------|------|
| **Development (DEV)** | local / dev | Active coding, fast inner loop | Individual developers | Synthetic / seeded |
| **Test / QA / Integration** | test, CI | Automated test suites, integration checks | CI pipeline, QA | Synthetic, reset often |
| **Staging / Homologation (HML)** | staging, UAT, pre-prod | Final validation against a production replica; sign-off | QA, PO, business | Production-like (masked) |
| **Production (PROD)** | prod, live | Serves real users | End users | Real |

**Staging is the critical gate.** It is "a near-perfect replica of your production environment where you test applications before deploying them to live users — the final checkpoint that catches bugs, performance issues, and integration problems before they reach production" ([Northflank — What is a staging environment](https://northflank.com/blog/what-is-a-staging-environment-how-to-set-one-up)).

### Environment parity (the 12-factor mandate)
The dangerous gaps between environments are time, personnel, and tools. The fix is **dev/prod parity**: keep all environments as similar as possible, and crucially — *"all deploys of the app (developer environments, staging, production) should be using the same type and version of each of the backing services"* ([The Twelve-Factor App — Dev/prod parity](https://12factor.net/dev-prod-parity)). If prod runs PostgreSQL 16, your laptop should not run SQLite "because it's easier." The divergence is exactly where "works on my machine" bugs breed.

Practical ways to enforce parity ([Northflank](https://northflank.com/blog/what-is-a-staging-environment-how-to-set-one-up)):

- **Infrastructure as Code (IaC)** so every environment is built from the same definitions — no hand-tuned snowflakes.
- **Containers** so the runtime is identical across machines.
- **Automated, scheduled refreshes** of staging data/config from production (masked) to prevent drift.
- **Ephemeral environments** that can be torn down and rebuilt quickly, eliminating stale state.

### Environment isolation
Environments must be **isolated** so a mistake in one cannot touch another. At the strongest level this means **separate cloud accounts/subscriptions per environment** (e.g., separate AWS accounts via AWS Organizations) so a breach or fat-finger in staging is contained at the account boundary, not just the service level ([Staging vs Production — isolation discussion](https://www.youtube.com/watch?v=A1E6P7U_nrk)). At minimum: separate networks, separate credentials, separate databases.

---

## 2. Where configuration lives: config in the environment

The 12-factor rule: **store config in environment variables**, read at runtime ([The Twelve-Factor App — Config](https://12factor.net/config)).

Why env vars specifically ([12factor.net/config](https://12factor.net/config); [DreamFactory — 12-factor](https://www.dreamfactory.com/resources/whitepapers/implementing-the-twelve-factor-app-methodology)):

- **Easy to change between deploys** without touching code.
- **Little chance of accidental commit** to the repo (unlike a config file you might `git add`).
- **Language- and OS-agnostic** — a universal standard supported by every stack, container, VM, and serverless runtime.
- **One build, many environments** — the same artifact reads the DB connection string from the environment, which differs per deploy ([DreamFactory](https://www.dreamfactory.com/resources/whitepapers/implementing-the-twelve-factor-app-methodology)).

A subtle but important 12-factor point: env vars are **granular and orthogonal** — managed independently per deploy, *not* bundled into named "environment" groups baked into the app ([12factor.net/config](https://12factor.net/config)). The app shouldn't have a hardcoded notion of "the staging config blob"; it should read individual values that happen to be set to staging's values in the staging deploy.

### The pragmatic layered reality
In practice (and this is fine), most stacks support **layered configuration** with a clear precedence order. A common, defensible pattern:

1. **Committed defaults** for non-sensitive settings (e.g., a base config file checked into the repo) — feature toggles, timeouts, log levels.
2. **Environment-specific overrides** layered on top.
3. **Environment variables** override files, and carry anything sensitive or deploy-specific.
4. **A secrets manager** supplies the actual secret *values* (see §3).

This mirrors how real teams operate: non-secret defaults in config files, with env vars taking precedence and supplying secrets ([r/dotnet — 12-factor in practice](https://www.reddit.com/r/dotnet/comments/1ayejq8/twelvefactor_app_in_net_questions/)). The rule that doesn't bend: **secrets never live in committed config.**

### Where config (the non-secret part) is version-controlled
Config *scripts/definitions* for each environment can and should live in version control — but in a **separate scope from the app code** (e.g., an infra/config repo, or a Kubernetes ConfigMap per environment that deploys independently of the app) ([HN discussion on 12-factor config](https://news.ycombinator.com/item?id=21416106)). The boundary: **the environment/infrastructure owns the config data, not the application code.**

---

## 3. Secrets: the one thing that must never touch git

Configuration splits into two classes, treated very differently:

- **Non-secret config** — DB host, port, feature flags, log level, timeouts. Can live in env vars and version-controlled config.
- **Secrets** — DB passwords, API keys, tokens, private keys, connection strings *containing* credentials. These get special handling.

### The cardinal rule
**Never store unencrypted secrets in a git repository** ([GitGuardian — Secrets management best practices](https://blog.gitguardian.com/secrets-api-management/)). This is the most common and most damaging mistake in the industry. Once a secret is committed, it is in the git history *forever* — deleting the file doesn't remove it from past commits.

Defensive baseline ([GitGuardian](https://blog.gitguardian.com/secrets-api-management/); [r/devops — secrets in git](https://www.reddit.com/r/devops/comments/owfipu/question_about_secrets_inside_git_repositories/)):

- Add `.env`, `*.config` with secrets, key files, and data extracts to **`.gitignore`** in every repo.
- **Don't rely on code review to catch secrets** — use **automated secret scanning** (and ideally a pre-receive/pre-commit hook that rejects pushes containing secret-shaped strings).
- **Never share secrets unencrypted** in Slack/email/tickets.
- If a secret leaks, **rotate it immediately** — that's the first order of business, not cleanup ([r/devops](https://www.reddit.com/r/devops/comments/owfipu/question_about_secrets_inside_git_repositories/)).

### The right home for secrets: a secrets manager
Use a **dedicated secrets management system** as the source of truth — HashiCorp Vault, AWS Secrets Manager / KMS, Azure Key Vault, GCP Secret Manager, Doppler, etc. ([GitGuardian](https://blog.gitguardian.com/secrets-api-management/); [r/devops](https://www.reddit.com/r/devops/comments/owfipu/question_about_secrets_inside_git_repositories/)). A secrets manager gives you what env vars alone cannot:

- **Centralized storage** and a single place to create/rotate/revoke ([Doppler — secrets as code](https://www.doppler.com/blog/store-secrets-as-code-what-works-and-doesnt)).
- **Access control (RBAC)**, **access logging/audit**, and **versioning** of secret values ([r/devops](https://www.reddit.com/r/devops/comments/owfipu/question_about_secrets_inside_git_repositories/)).
- **Pipeline/runtime integration** — secrets are delivered to the running app automatically at deploy/runtime.

### The modern secret-handling model
Doppler's distilled best practice: *"centralize secrets in a manager, keep them out of Git when possible, fetch them only at runtime, and tightly scope and rotate access"* ([Doppler](https://www.doppler.com/blog/store-secrets-as-code-what-works-and-doesnt)). Concretely:

- **Fetch at runtime, not build time.** Don't bake secrets into Docker images, AMIs, or binaries — they should exist only in the process that needs them, only when needed ([Doppler](https://www.doppler.com/blog/store-secrets-as-code-what-works-and-doesnt)).
- **Scope tightly.** A DB credential should work only for the service that needs it; a CI job gets only the variables for that run ([Doppler](https://www.doppler.com/blog/store-secrets-as-code-what-works-and-doesnt)).
- **Rotate on a schedule** and pull the latest version at deploy time ([Doppler](https://www.doppler.com/blog/store-secrets-as-code-what-works-and-doesnt)).
- **Isolate per environment** — dev/staging/prod secrets are separate, with separate access ([Doppler](https://www.doppler.com/blog/store-secrets-as-code-what-works-and-doesnt)).

### If you must keep secrets near code
When a workflow genuinely requires secrets in the repo (e.g., GitOps), **encrypt them** with tooling like **Mozilla SOPS**, **git-secret**, **ansible-vault**, or **Kubernetes Sealed Secrets**, and commit only the encrypted blob ([GitGuardian](https://blog.gitguardian.com/secrets-api-management/); [Doppler](https://www.doppler.com/blog/store-secrets-as-code-what-works-and-doesnt)). IaC should *reference* the manager; the secret *values* live in secure storage, never in the IaC source ([Doppler](https://www.doppler.com/blog/store-secrets-as-code-what-works-and-doesnt)).

### Local development
For the local inner loop, a `.gitignored` `.env` file or the stack's built-in local-secret store (e.g., per-OS user secret stores) is acceptable — these never leave the developer's machine and never hold production secrets ([r/dotnet](https://www.reddit.com/r/dotnet/comments/1ayejq8/twelvefactor_app_in_net_questions/)).

---

## 4. Connecting to a SQL server across DEV / HML / PROD

This is the concrete payoff: how an app reaches its database in each environment, securely.

### Principle 1 — A separate database (ideally a separate server) per environment
Never point staging and production at the same database. The accepted guidance: each environment gets its own database, and ideally its own server — *"this should really be a separate server, or if not possible, a separate database with proper permission boundaries"* ([r/dotnet — same DB for staging and prod](https://www.reddit.com/r/dotnet/comments/zalv01/same_database_for_staging_and_prod/)). Sharing a DB across environments means a staging bug can corrupt or leak production data.

### Principle 2 — The connection target comes from config, the credential from the secrets manager
The application is given, per environment:

- **Non-secret connection info** (host, port, database name) — from environment variables / config. This is what makes "one build, many environments" work: the same artifact connects to `db-dev`, `db-hml`, or `db-prod` purely based on injected config ([DreamFactory](https://www.dreamfactory.com/resources/whitepapers/implementing-the-twelve-factor-app-methodology)).
- **The credential** (password or, better, a token) — fetched at runtime from the secrets manager, never hardcoded, never in the repo (§3).

Treat the database as an **attached resource** (another 12-factor tenet): the app reaches it through a connection string in config, so the backing DB can be swapped per deploy without code changes ([rdegges — Dev/Prod Parity](https://rdegges.com/2012/a-developers-conundrum-dev-prod-parity/)).

### Principle 3 — Least privilege, scoped per environment and per service
Each service's DB account should have the **minimum permissions** it needs and nothing more. Don't let an app log in as a DB superuser. Scope credentials so a single leaked credential has a small blast radius ([Doppler](https://www.doppler.com/blog/store-secrets-as-code-what-works-and-doesnt); [GitGuardian](https://blog.gitguardian.com/secrets-api-management/)).

### Principle 4 — Prefer identity-based / ephemeral access over static passwords
The modern direction is to **eliminate long-lived static credentials**. Instead of storing a permanent DB password, the workload authenticates with **its own identity** (e.g., a cloud managed identity / IAM role / workload identity) and receives a **short-lived, automatically-expiring credential** ([Aembit — least privilege & static credentials](https://aembit.io/blog/why-devops-struggles-least-privilege-static-credentials-2025/)). This removes the entire "store and rotate the DB password" problem: there's no standing secret to leak, and the credential is precisely scoped and time-limited ([Aembit](https://aembit.io/blog/why-devops-struggles-least-privilege-static-credentials-2025/)). Vault's dynamic database secrets are the on-prem equivalent. Where static passwords remain, automate **rotation** ([OLOID — credential rotation](https://www.oloid.com/blog/credential-rotation); [Doppler](https://www.doppler.com/blog/store-secrets-as-code-what-works-and-doesnt)).

### Principle 5 — Lock down production access (humans included)
Production — and especially the production database — should be the most locked-down environment. Developers can be given broad access to **staging**, but production should be access-controlled such that "even developers ... nobody can really access it, especially the database" without explicit, audited, controlled access ([Staging vs Production](https://www.youtube.com/watch?v=A1E6P7U_nrk)). For the cases where a human genuinely needs production data ([r/devops — prod DB access](https://www.reddit.com/r/devops/comments/11fmo4l/how_do_you_deal_with_developers_asking_for/)):

- Grant **selective, read-only** access via **RBAC**, not blanket admin.
- Use **detective controls** — DB audit logs of who accessed what.
- Prefer **automatically-generated one-time accounts** or vaulted, rotated credentials over shared standing logins.
- **Network-isolate** the DB so all access flows through controlled access points (bastion/jump hosts), never directly from a laptop.

### Putting it together — request flow per environment
1. Deploy reads its **environment** (dev/hml/prod) → determines which config set applies.
2. App reads **host/port/dbname** from env vars/config (the non-secret target).
3. App authenticates: ideally via its **managed identity** to the secrets manager, fetches a **short-lived DB credential** (or, in legacy setups, a rotated password) at **runtime**.
4. App connects with a **least-privilege** account scoped to that one service in that one environment.
5. All access (especially prod) is **logged and auditable**; the DB sits behind network controls.

---

## 5. Database change management across environments

Schema and data changes must flow through the same environment ladder as code, but with their own discipline.

### Migrations are version-controlled, ordered, and tool-managed
Schema changes are expressed as **versioned migration scripts** committed alongside (but logically separate from) the app, applied by a dedicated migration tool (Flyway, Liquibase, Sqitch, EF Core Migrations, Alembic, etc.). Use a **single migration tool** consistently to avoid compatibility chaos ([X]Cube Labs — DB migration guide](https://www.xcubelabs.com/blog/database-migration-and-version-control-the-ultimate-guide-for-beginners/); [Liquibase — Schema migration guide](https://www.liquibase.com/resources/guides/database-schema-migration)). (The expand/migrate/contract technique for zero-downtime schema changes is covered in [file 17 — Database Design](17-database-design.md).)

### Separate the DB deployment pipeline from the app deployment
A strong pattern is to **keep schema changes distinct from application deployments** — effectively two pipelines, one for the app and one for the database ([r/devops — schema updates](https://www.reddit.com/r/devops/comments/1iwy2su/best_practices_for_managing_schema_updates_during/)). This lets you apply backward-compatible schema changes *before* the app that needs them, which is the foundation of zero-downtime deploys.

### Promote and test changes through the ladder
Apply each migration in **dev → test → staging** and validate it multiple times before it touches production, so the *change process itself* is rehearsed, not just the result ([Liquibase](https://www.liquibase.com/resources/guides/database-schema-migration)). Pre-production testing is where migration risk is bought down ([Liquibase](https://www.liquibase.com/resources/guides/database-schema-migration)).

### Always have a tested rollback and a backup
Before any production migration ([r/devops](https://www.reddit.com/r/devops/comments/1iwy2su/best_practices_for_managing_schema_updates_during/); [Liquibase](https://www.liquibase.com/resources/guides/database-schema-migration)):

- Prefer **backward-compatible changes** so the old app keeps working during/after the change.
- Write and **test down-migration scripts**; don't trust automatic rollbacks for production *data*.
- Take a **backup** first; verify backup/recovery procedures regularly.
- Detect **drift** — flag out-of-process changes made directly against a database so they don't silently diverge from the tracked schema ([Liquibase](https://www.liquibase.com/resources/guides/database-schema-migration)).

### Staging data must be production-like but safe
Staging should hold **production-like data** for realistic testing, but with sensitive fields **masked/anonymized**, and refreshed on a schedule to avoid drift ([Northflank](https://northflank.com/blog/what-is-a-staging-environment-how-to-set-one-up)). Never copy raw production PII into a lower environment.

---

## 6. A reference checklist

**Environments**
- Separate, isolated DEV / TEST / HML / PROD — ideally separate accounts/subscriptions.
- Same type & version of every backing service across environments (parity).
- Environments built from IaC; staging refreshed from prod (masked) on a schedule.

**Config**
- One build artifact; all environment differences come from injected config.
- Non-secret config in env vars (and version-controlled config in a *separate* scope from app code).
- No hardcoded environment-specific values in the app.

**Secrets**
- Nothing secret in git — `.gitignore` + automated secret scanning + push protection.
- Secrets manager is the source of truth; fetch at runtime, scope tightly, rotate, isolate per env.
- Leaked secret → rotate immediately.
- If secrets must be near code, store them encrypted (SOPS/Sealed Secrets), never plaintext.

**Database access**
- One database (ideally one server) per environment; never share across envs.
- Connection target from config; credential from the secrets manager at runtime.
- Least-privilege, per-service, per-environment DB accounts.
- Prefer managed-identity / short-lived credentials over static passwords; rotate what remains.
- Production DB locked down: RBAC read-only for humans, audit logs, one-time/vaulted creds, network isolation.

**DB changes**
- Versioned migrations via one consistent tool, committed and code-reviewed.
- Separate DB pipeline from app pipeline; apply backward-compatible changes first.
- Promote dev → test → staging before prod; backup + tested rollback before every prod migration; watch for drift.

---

## Key sources

- [The Twelve-Factor App — Config](https://12factor.net/config) and [Dev/prod parity](https://12factor.net/dev-prod-parity) — the foundational principles: config in the environment, and keep environments alike (same backing-service versions).
- [DreamFactory — Implementing the Twelve-Factor App](https://www.dreamfactory.com/resources/whitepapers/implementing-the-twelve-factor-app-methodology) and [rdegges — A Developer's Conundrum: Dev/Prod Parity](https://rdegges.com/2012/a-developers-conundrum-dev-prod-parity/) — config as env vars, DB as an attached resource.
- [GitGuardian — Secrets management best practices](https://blog.gitguardian.com/secrets-api-management/) and [Doppler — Should you store secrets as code?](https://www.doppler.com/blog/store-secrets-as-code-what-works-and-doesnt) — never commit secrets, centralize in a manager, fetch at runtime, scope & rotate.
- [Aembit — Why DevOps still struggles with least privilege](https://aembit.io/blog/why-devops-struggles-least-privilege-static-credentials-2025/) and [OLOID — Credential Rotation](https://www.oloid.com/blog/credential-rotation) — eliminating static credentials via ephemeral, identity-based access.
- [Northflank — What is a staging environment](https://northflank.com/blog/what-is-a-staging-environment-how-to-set-one-up) — staging as a production replica, parity automation, masked data.
- [r/dotnet — same DB for staging and prod](https://www.reddit.com/r/dotnet/comments/zalv01/same_database_for_staging_and_prod/) and [r/devops — production DB access](https://www.reddit.com/r/devops/comments/11fmo4l/how_do_you_deal_with_developers_asking_for/) — separate DBs per environment; locking down prod access (RBAC, audit, jump hosts).
- [Liquibase — Database Schema Migration](https://www.liquibase.com/resources/guides/database-schema-migration) and [r/devops — schema updates during deployment](https://www.reddit.com/r/devops/comments/1iwy2su/best_practices_for_managing_schema_updates_during/) — versioned migrations, separate DB pipeline, rollback/backup discipline, drift detection.
