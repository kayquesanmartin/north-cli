# 18 — Cybersecurity for Developers

Security is not a feature you add at the end or a separate team's problem — it is a property of how you design, build, and operate every part of the system. The good news: a developer who internalizes a handful of principles and the most common vulnerability classes prevents the overwhelming majority of real-world breaches. This file is the working baseline; [file 12 §6](12-scalability-reliability.md) introduced it, this goes deeper.

---

## 1. The OWASP Top 10 — the vulnerabilities you must know

The [OWASP Top 10](https://owasp.org/www-project-top-ten/) is the industry-standard awareness document for the most critical web application security risks ([Black Duck — What is the OWASP Top 10](https://www.blackduck.com/glossary/what-is-owasp-top-10.html)). The **2021** list ([OWASP Top 10:2021](https://owasp.org/Top10/2021/)):

1. **A01 Broken Access Control** — users acting outside their permissions (e.g., changing an `id` in a URL to read another user's data — IDOR). *The #1 risk.* Enforce authorization **server-side on every request**, deny by default.
2. **A02 Cryptographic Failures** — sensitive data exposed through weak/missing crypto. Encrypt in transit (TLS) and at rest; never roll your own crypto; hash passwords with **bcrypt/argon2/scrypt** (slow, salted), never MD5/SHA-1 or reversible encryption.
3. **A03 Injection** — SQL, NoSQL, OS command, LDAP injection when untrusted input is interpreted as code. Fix: **parameterized queries / prepared statements**, never string concatenation; validate input; escape appropriately. (XSS folded into this category in 2021.)
4. **A04 Insecure Design** — flaws in the design itself, not the implementation. Mitigated by **threat modeling**, secure design patterns, and reference architectures *before* coding.
5. **A05 Security Misconfiguration** — default credentials, verbose errors, open cloud buckets, unnecessary features enabled. Harden defaults; automate configuration.
6. **A06 Vulnerable & Outdated Components** — using libraries with known CVEs. Identify and patch them; evaluate stale/malicious packages for the risk they introduce ([Black Duck](https://www.blackduck.com/glossary/what-is-owasp-top-10.html)). Use SCA tooling (Dependabot, Snyk).
7. **A07 Identification & Authentication Failures** — broken auth/session management lets attackers compromise passwords, keys, and sessions → identity theft ([Black Duck](https://www.blackduck.com/glossary/what-is-owasp-top-10.html)). Use proven identity providers, MFA, secure session handling.
8. **A08 Software & Data Integrity Failures** — trusting unverified updates, plugins, or CI/CD pipelines (supply-chain attacks). Verify signatures; secure the build pipeline.
9. **A09 Security Logging & Monitoring Failures** — without logging/alerting, breaches go undetected for months. Log security-relevant events; alert on anomalies ([file 12 observability](12-scalability-reliability.md)).
10. **A10 Server-Side Request Forgery (SSRF)** — the server is tricked into making requests to unintended (often internal) destinations. Validate/allow-list outbound URLs; segment networks.

> Memorize the *shape* of these ten. Most CVEs and most code-review security findings map directly onto one of them.

---

## 2. Foundational principles

These outlast any specific vulnerability list:

- **Defense in depth** — multiple independent layers; assume any single control can fail.
- **Least privilege** — every user, service, token, and DB account gets the minimum access needed, and no more. The blast radius of a compromise equals the privileges it held.
- **Secure defaults / fail securely** — the default configuration is the safe one; on error, deny rather than allow. Don't ship debug mode or default passwords.
- **Never trust input** — validate (allow-list, not block-list) all external input at the boundary; **encode output** for its destination context (HTML, SQL, shell, URL).
- **Don't roll your own crypto / auth** — use vetted libraries and identity providers. This is the single most reliable way to avoid A02/A07.
- **Minimize attack surface** — fewer endpoints, fewer features enabled, fewer dependencies = less to exploit.
- **Complete mediation** — check authorization on *every* access, not just the first; don't cache an allow decision insecurely.

---

## 3. AuthN vs AuthZ (get the vocabulary right)

- **Authentication (AuthN)** — *who are you?* Passwords + MFA, OAuth2/OIDC, SSO, mTLS, API keys. Validate tokens (signature, expiry, audience) on every request.
- **Authorization (AuthZ)** — *what may you do?* RBAC (roles) or ABAC (attributes/policies). Enforce in the service, not just the UI or gateway — the gateway is convenience, the service is truth ([file 11](11-api-design.md)).
- **Sessions vs tokens** — server sessions (stateful, easy to revoke) vs JWTs (stateless, scalable, but hard to revoke — keep them short-lived and pair with refresh tokens).

---

## 4. Data protection

- **In transit:** TLS everywhere, including internal service-to-service (don't assume the network is trusted — zero trust).
- **At rest:** disk/column encryption; encrypt secrets and PII.
- **Secrets management:** never in code, config files, or container images ([12-factor config](12-scalability-reliability.md)). Use a vault (HashiCorp Vault, AWS Secrets Manager, etc.), inject at runtime, and **rotate** regularly.
- **PII & compliance:** know your obligations — **LGPD** (Brazil), **GDPR** (EU), **CCPA**, **PCI-DSS** for cards. Data minimization, purpose limitation, and the right to deletion shape your data model ([file 17](17-database-design.md)).
- **Hashing vs encryption:** hash (one-way) for passwords; encrypt (reversible) only when you must read the data back.

---

## 5. Building security into the lifecycle (DevSecOps)

Shift security **left** — earlier and continuous, not a pre-launch gate:
- **Threat modeling** during design (STRIDE is a usable framework) — addresses A04 before code exists.
- **SAST** (static analysis) and **secret scanning** in CI on every PR.
- **SCA** (dependency scanning) to catch vulnerable components (A06).
- **DAST** (dynamic testing) against running environments.
- **Code review with a security lens** — does this endpoint check authorization? Is this query parameterized?
- **Penetration testing** for high-risk systems before major releases.
- **Patch management** — a CVE in a transitive dependency is *your* vulnerability; keep dependencies current.

> For AI-assisted development ([file 14](14-spec-driven-development.md)): treat agent-generated code as untrusted until reviewed. Agents reproduce insecure patterns from their training data (string-concatenated SQL, missing authz checks). Put security requirements in your `AGENTS.md`/constitution and review generated code against the Top 10.

---

## 6. A pragmatic developer checklist

- [ ] All DB access uses parameterized queries (no string-built SQL).
- [ ] Every endpoint enforces authentication *and* authorization server-side.
- [ ] All input validated (allow-list); all output encoded for its context.
- [ ] TLS on all connections; secrets in a vault, never in code/repo.
- [ ] Passwords hashed with bcrypt/argon2; MFA available for sensitive accounts.
- [ ] Dependencies scanned and patched; lockfiles committed.
- [ ] Security-relevant events logged; alerts configured.
- [ ] Errors don't leak stack traces, secrets, or internal details to clients.
- [ ] Rate limiting and quotas on public endpoints.
- [ ] Threat model reviewed for anything handling money, PII, or auth.

---

## Key sources
- [OWASP Top Ten — project home](https://owasp.org/www-project-top-ten/) and [OWASP Top 10:2021](https://owasp.org/Top10/2021/).
- [What Is the OWASP Top 10 and How Does It Work — Black Duck](https://www.blackduck.com/glossary/what-is-owasp-top-10.html).
- OWASP Cheat Sheet Series and *Web Application Security* (Hoffman); see [file 13](13-reading-list.md).
