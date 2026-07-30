# Inventory API

**Personal Inventory / Asset Tracker** — Educational REST API project.

Stack: **FastAPI · PostgreSQL · Redis · Jinja2 · Docker Compose**

This project was built to practice **real REST API design** (resource modeling, HTTP semantics, authorization per resource) together with **secure authentication** aligned with OWASP considerations.

---

## Quick Start

```bash
git clone https://github.com/bbarbosa-lab/inventory-api.git
cd inventory-api
cp .env.example .env
docker compose up --build
```

Open:

| URL | Description |
|-----|-------------|
| http://localhost:8000 | Home |
| http://localhost:8000/register | Create account |
| http://localhost:8000/login | Login |
| http://localhost:8000/dashboard | Protected area |
| http://localhost:8000/docs | Swagger (API) |

---

## What this project teaches

1. **Resource-oriented design** (Items, Categories, Locations, Movements)
2. Correct use of HTTP methods and status codes
3. Authorization **per resource** (ownership checks — anti-IDOR)
4. Secure authentication flows (register, login, logout, password reset)
5. Server-rendered pages + JSON API in the same application
6. Security controls mapped to OWASP Top 10 concerns

See:
- [`docs/DESIGN.md`](docs/DESIGN.md) — why this API is (and is not fully) REST
- [`docs/SECURITY.md`](docs/SECURITY.md) — OWASP-oriented controls

---

## Core Resources (API)

| Resource | Collection | Item |
|----------|------------|------|
| Items | `GET/POST /api/items` | `GET/PATCH/DELETE /api/items/{id}` |
| Categories | `GET/POST /api/categories` | `GET/DELETE /api/categories/{id}` |
| Locations | `GET/POST /api/locations` | `GET/DELETE /api/locations/{id}` |
| Movements | `GET/POST /api/items/{id}/movements` | — |

Auth:

- `POST /api/auth/register`
- `POST /api/auth/login`
- `POST /api/auth/logout`
- `GET  /api/auth/me`
- `POST /api/auth/password-reset/request`
- `POST /api/auth/password-reset/confirm`
- `POST /api/auth/change-password`

---

## Example API usage

```bash
# Register
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@example.com","password":"CorrectHorseBattery1!","display_name":"Alice"}'

# Login (stores session cookie)
curl -c cookies.txt -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@example.com","password":"CorrectHorseBattery1!"}'

# Create item
curl -b cookies.txt -X POST http://localhost:8000/api/items \
  -H "Content-Type: application/json" \
  -d '{"name":"Notebook Dell","status":"available","quantity":1}'

# List items
curl -b cookies.txt http://localhost:8000/api/items
```

---

## Architecture

```
Browser / API Client
        │
        ▼
FastAPI (auth + inventory routers + Jinja pages)
        │
   ┌────┴────┐
   ▼         ▼
PostgreSQL  Redis
(identity +  (sessions +
inventory)   rate limits)
```

- **PostgreSQL**: durable identity and inventory data
- **Redis**: opaque sessions, rate-limit counters, password-reset tokens

---

## Security highlights

- argon2id password hashing (64 MiB, t=3, p=4)
- Server-side sessions with regeneration on login (anti-fixation)
- Rate limiting (IP + account) + temporary lockout
- Uniform error messages (anti-enumeration)
- Ownership checks on every inventory resource (anti-IDOR)
- Security headers (CSP, X-Frame-Options, etc.)
- Password reset tokens are single-use and short-lived

Details in [`docs/SECURITY.md`](docs/SECURITY.md).

---

## Project structure

```
app/
  core/          # config, database, security, deps
  models/        # SQLAlchemy models
  schemas/       # Pydantic
  routers/       # auth, items, categories, locations, pages
  templates/     # Jinja2 HTML
  static/        # CSS
docs/
  DESIGN.md      # REST design decisions
  SECURITY.md    # OWASP mapping
docker-compose.yml
Dockerfile
requirements.txt
```

---

## License / Intent

Educational / portfolio artifact focused on learning proper REST API design and secure authentication.  
Not a drop-in production inventory system without further hardening (MFA, email delivery, monitoring, etc.).
