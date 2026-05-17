"""
Resolve authenticated end-user id from gateway headers (Kinde sub / id).
"""

from __future__ import annotations

from typing import Optional

from fastapi import Header


async def resolve_owner_user_id(
    x_user_id: Optional[str] = Header(None, alias="X-User-ID"),
    x_user_email: Optional[str] = Header(None, alias="X-User-Email"),
) -> str:
    """
    Priority:
    1) X-User-ID (Kinde id / sub)
    2) X-User-Email (fallback for older clients)
    3) anonymous (shared bucket — not recommended for production)
    """
    if x_user_id and x_user_id.strip():
        return x_user_id.strip()[:256]
    if x_user_email and x_user_email.strip():
        return x_user_email.strip().lower()[:256]
    return "anonymous"
