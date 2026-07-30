# DESIGN.md — REST Design Decisions

This document explains **how and why** this API was modeled, and where it intentionally deviates from pure REST (Fielding).

## Goal of the project

Practice **resource-oriented HTTP API design** with:

- Clear resources and collections
- Correct HTTP method semantics
- Authorization per resource
- Predictable status codes
- Honest documentation of trade-offs

---

## Resources identified

| Resource | Meaning |
|----------|---------|
| **User** | Identity (owner of inventory data) |
| **Item** | An asset/equipment entry |
| **Category** | Classification of items |
| **Location** | Physical or logical place |
| **Movement** | Historical change related to an item |

These are **nouns** (resources), not actions.

---

## URI design

```
/api/items
/api/items/{id}
/api/items/{id}/movements

/api/categories
/api/categories/{id}

/api/locations
/api/locations/{id}

/api/auth/*          # authentication actions (RPC-style by nature)
```

### Why nested `/items/{id}/movements`?

A movement always belongs to an item. Nesting communicates the ownership relationship and keeps the collection scoped. This is still resource-oriented (movements are resources), not an RPC verb.

---

## HTTP methods used

| Method | Usage in this API |
|--------|-------------------|
| `GET` | Retrieve representation of resource or collection |
| `POST` | Create a subordinate resource |
| `PATCH` | Partial update of an item |
| `DELETE` | Remove a resource |

We avoid `PUT` for partial updates. `PATCH` is more precise for the fields we allow to change.

---

## Status codes

| Code | When |
|------|------|
| 200 | Successful GET / PATCH |
| 201 | Resource created (`POST`) |
| 204 | Successful DELETE |
| 400 | Invalid input / business rule |
| 401 | Not authenticated |
| 404 | Resource not found **or** not owned by the caller (anti-enumeration of foreign IDs) |
| 422 | Validation error (Pydantic) |
| 429 | Rate limited |

Returning `404` for both “does not exist” and “exists but you don’t own it” reduces leaking information about other users’ resources.

---

## Authorization model

Every inventory endpoint calls an ownership check:

```text
item.owner_id == current_user.id
```

This is **object-level authorization**.  
Being authenticated is not enough — the user must own the specific resource.

This directly mitigates **IDOR / BOLA** (OWASP API Security).

---

## Does this project “meet REST”?

### What it does well (REST-aligned)

1. **Resource identification** via stable URIs
2. **Manipulation through representations** (JSON)
3. **Self-descriptive messages** (HTTP methods + status codes + JSON body)
4. **Client-Server** separation
5. Clear collection vs item distinction
6. Filtering and pagination parameters on collections

### Intentional deviations / limitations

1. **Stateless constraint is not fully met**  
   Authentication uses **server-side sessions in Redis** (opaque session ID in cookie).  
   This is a pragmatic choice for browser-based flows and matches common secure web app patterns.  
   A pure REST approach would prefer fully stateless tokens (e.g. JWT) carried on every request.

2. **HATEOAS is not implemented**  
   Responses do not include hypermedia links. Clients must know the URI structure.  
   This is the common industry trade-off; full HATEOAS is rare in commercial APIs.

3. **Auth endpoints are action-oriented**  
   `/api/auth/login`, `/logout`, `/password-reset/*` are naturally RPC-style.  
   Authentication flows rarely map cleanly to pure resources; this is accepted.

### Summary judgment

This is a **resource-oriented HTTP API** with strong ownership semantics and correct use of methods/status codes.  
It is **not pure Fielding REST** because of sessions and lack of HATEOAS.  
The design is honest, educational, and suitable for real learning of REST principles.

---

## How to extend toward stricter REST

1. Replace sessions with stateless bearer tokens (JWT or similar).
2. Add `Link` headers or `_links` objects in representations.
3. Introduce explicit API versioning (`/api/v1/...`).
4. Adopt RFC 7807 problem details for errors.
5. Consider cursor-based pagination for large collections.

---

## Learning questions this design forces you to answer

- Why is `/items/{id}/move` a worse design than updating the item + recording a movement resource?
- Why return 404 instead of 403 when the item belongs to another user?
- What breaks if we allow one user to read another user’s category by ID?
- How would you model “transfer item to another user” as resources instead of an action?

Document your answers as you evolve the project.
