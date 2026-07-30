"""
Security primitives: password hashing (argon2id), sessions (Redis),
rate limiting and lockout helpers.

Designed with OWASP ASVS / Top 10 considerations in mind.
"""
from __future__ import annotations

import secrets
from datetime import datetime, timezone, timedelta
from typing import Any

import redis
from passlib.context import CryptContext

from app.core.config import get_settings

settings = get_settings()

pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
    argon2__memory_cost=65536,  # 64 MiB
    argon2__time_cost=3,
    argon2__parallelism=4,
)

_redis: redis.Redis | None = None


def get_redis() -> redis.Redis:
    global _redis
    if _redis is None:
        _redis = redis.from_url(settings.redis_url, decode_responses=True)
    return _redis


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return pwd_context.verify(plain, hashed)
    except Exception:
        return False


def generate_token(nbytes: int = 32) -> str:
    return secrets.token_urlsafe(nbytes)


# ---------- Sessions (server-side, opaque ID) ----------

def create_session(user_id: int, ip: str | None = None, ua: str | None = None) -> str:
    r = get_redis()
    sid = generate_token(32)
    key = f"session:{sid}"
    data = {
        "user_id": str(user_id),
        "ip": ip or "",
        "ua": (ua or "")[:200],
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    r.hset(key, mapping=data)
    r.expire(key, settings.session_ttl_seconds)
    return sid


def rotate_session(old_sid: str | None, user_id: int, ip: str | None = None, ua: str | None = None) -> str:
    """Issue a new session and destroy the old one (anti-fixation)."""
    if old_sid:
        destroy_session(old_sid)
    return create_session(user_id, ip=ip, ua=ua)


def get_session(sid: str | None) -> dict[str, Any] | None:
    if not sid:
        return None
    r = get_redis()
    data = r.hgetall(f"session:{sid}")
    if not data:
        return None
    # sliding expiration
    r.expire(f"session:{sid}", settings.session_ttl_seconds)
    return data


def destroy_session(sid: str) -> None:
    get_redis().delete(f"session:{sid}")


def destroy_all_user_sessions(user_id: int, except_sid: str | None = None) -> None:
    r = get_redis()
    for key in r.scan_iter(match="session:*"):
        data = r.hgetall(key)
        if data.get("user_id") == str(user_id):
            if except_sid and key == f"session:{except_sid}":
                continue
            r.delete(key)


# ---------- Rate limiting ----------

def check_rate(prefix: str, identifier: str, limit: int, window_seconds: int) -> tuple[bool, int]:
    """Returns (allowed, remaining)."""
    r = get_redis()
    key = f"rl:{prefix}:{identifier}"
    current = r.incr(key)
    if current == 1:
        r.expire(key, window_seconds)
    remaining = max(0, limit - current)
    return current <= limit, remaining


# ---------- Password reset tokens ----------

def store_reset_token(user_id: int, token: str, ttl_seconds: int = 3600) -> None:
    r = get_redis()
    r.setex(f"reset:{token}", ttl_seconds, str(user_id))


def consume_reset_token(token: str) -> int | None:
    r = get_redis()
    key = f"reset:{token}"
    uid = r.get(key)
    if not uid:
        return None
    r.delete(key)
    return int(uid)


def log_auth_event(event: str, email: str, ip: str) -> None:
    r = get_redis()
    entry = f"{datetime.now(timezone.utc).isoformat()}|{event}|{email}|{ip}"
    r.lpush("auth_events", entry)
    r.ltrim("auth_events", 0, 999)
