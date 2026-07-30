# SECURITY.md — OWASP-oriented controls

This document maps implemented controls to common risks (OWASP Top 10 / ASVS style thinking).

> No system is “OWASP compliant” by claim alone. This is an explicit mapping of **what was implemented** and **residual risk**.

---

## Authentication & Session Management

| Control | Implementation |
|---------|----------------|
| Password storage | argon2id (64 MiB memory, time=3, parallelism=4) via passlib |
| Session ID | Cryptographically random, opaque, stored only in Redis |
| Session fixation | Session ID regenerated on every successful login |
| Logout | Server-side session destroyed immediately |
| Cookie flags | HttpOnly, SameSite=Lax, Secure in production |
| Password policy | Minimum 12 characters (enforced in schema + route) |

---

## Brute force / Credential stuffing

| Control | Implementation |
|---------|----------------|
| Rate limit by IP | Redis counter on login/register/reset |
| Rate limit by account | Separate counter per email |
| Account lockout | Temporary lock after N failures |
| Timing | Dummy password verify path to reduce user-enumeration timing signal |
| Uniform messages | Same response for invalid user vs invalid password |

---

## Access Control (IDOR / BOLA)

| Control | Implementation |
|---------|----------------|
| Object-level authorization | Every item/category/location query filters by `owner_id == current_user.id` |
| Foreign resource | Returns **404** (not 403) to avoid leaking existence |

---

## Injection

| Control | Implementation |
|---------|----------------|
| SQL | SQLAlchemy ORM parameterized queries |
| Input validation | Pydantic schemas on all write endpoints |

---

## Security Misconfiguration / Headers

| Header | Value |
|--------|-------|
| X-Content-Type-Options | nosniff |
| X-Frame-Options | DENY |
| Content-Security-Policy | restrictive (default-src 'self', etc.) |
| Referrer-Policy | strict-origin-when-cross-origin |
| Cache-Control | no-store (auth-sensitive responses) |
| HSTS | enabled when `ENVIRONMENT=production` |

---

## Sensitive Data Exposure

- Passwords never logged or returned.
- Password-reset tokens are single-use and short-lived (Redis TTL).
- In `DEBUG=true`, reset token is returned in the response for local testing only — **must not happen in production**.

---

## CSRF

- SameSite=Lax cookies reduce risk for cross-site POST from foreign origins.
- API JSON endpoints expect `Content-Type: application/json` (not simple form posts from foreign sites).
- Residual risk remains for some legacy browser cases; double-submit token can be added later for form posts.

---

## Residual risks (honest)

1. No MFA / WebAuthn.
2. No real email delivery for password reset (token shown only in debug).
3. CSP allows `'unsafe-inline'` for small form handlers.
4. Session store (Redis) compromise allows session abuse — network isolation is required in real deployments.
5. Host/container compromise bypasses application controls.
6. Rate limits alone do not stop large distributed botnets (need WAF / CAPTCHA / reputation for high-threat environments).

---

## Mapping (simplified) to OWASP concerns

| Area | Status in this project |
|------|------------------------|
| Broken Access Control | Mitigated with ownership checks |
| Cryptographic Failures | argon2id + no plaintext secrets in responses |
| Injection | ORM + validation |
| Insecure Design | Explicit threat-aware auth flows |
| Security Misconfiguration | Security headers + least debug exposure |
| Identification & Auth Failures | Rate limit, lockout, fixation protection, uniform errors |
| SSRF / etc. | Not applicable to current surface |

This is a **learning-grade secure baseline**, not a production certification claim.
