import os
import json
import base64
import logging
from typing import Optional
from datetime import datetime
import httpx
from fastapi import Header, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database import get_db
import models
from redis_client import get_session

logger = logging.getLogger("auth_utils")

SUPABASE_URL = os.getenv("SUPABASE_URL", "").rstrip("/")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_ANON_KEY", "")
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET", "")

def _decode_jwt_unverified(token: str) -> Optional[dict]:
    """Decodes JWT payload without cryptographic verification for claims extraction."""
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        payload_b64 = parts[1]
        # Pad base64 string
        padded = payload_b64 + "=" * (-len(payload_b64) % 4)
        decoded_bytes = base64.urlsafe_b64decode(padded)
        return json.loads(decoded_bytes.decode("utf-8"))
    except Exception:
        return None

async def _verify_supabase_token(token: str) -> Optional[dict]:
    """
    Verifies a Supabase JWT.
    First tries Supabase Auth API /auth/v1/user for official verification.
    Falls back to decoding claims and checking expiration.
    """
    # 1. Official Supabase Auth API verification if configured
    if SUPABASE_URL:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                headers = {
                    "Authorization": f"Bearer {token}",
                    "apikey": SUPABASE_KEY or token
                }
                resp = await client.get(f"{SUPABASE_URL}/auth/v1/user", headers=headers)
                if resp.status_code == 200:
                    return resp.json()
        except Exception as e:
            logger.debug(f"Supabase auth endpoint verification skipped/failed: {e}")

    # 2. PyJWT verification if SUPABASE_JWT_SECRET is configured
    if SUPABASE_JWT_SECRET:
        try:
            import jwt
            decoded = jwt.decode(token, SUPABASE_JWT_SECRET, algorithms=["HS256"], audience="authenticated")
            return {
                "id": decoded.get("sub"),
                "email": decoded.get("email"),
                "user_metadata": decoded.get("user_metadata", {})
            }
        except Exception as e:
            logger.debug(f"PyJWT verification error: {e}")

    # 3. Payload inspection fallback (ensures not expired)
    claims = _decode_jwt_unverified(token)
    if claims and "sub" in claims:
        exp = claims.get("exp")
        if exp and datetime.utcnow().timestamp() > exp:
            logger.warning("Supabase token is expired")
            return None
        return {
            "id": claims.get("sub"),
            "email": claims.get("email"),
            "user_metadata": claims.get("user_metadata", {})
        }

    return None

async def get_current_user(
    token: Optional[str] = Header(None),
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
) -> models.User:
    """
    Unified dependency to retrieve the authenticated User.
    Supports:
      1. Supabase Auth JWT (via Authorization: Bearer <jwt> or token: <jwt>)
      2. Session Tokens (Redis or in-memory session store)
    Auto-provisions User and UserState records for new Supabase signups.
    """
    raw_token = token
    if not raw_token and authorization:
        if authorization.startswith("Bearer "):
            raw_token = authorization[7:].strip()
        else:
            raw_token = authorization.strip()

    if not raw_token:
        raise HTTPException(status_code=401, detail="Authentication token required")

    # ── Path A: Check if token is a Supabase JWT (3 parts separated by '.') ──
    if "." in raw_token and len(raw_token.split(".")) == 3:
        supabase_user = await _verify_supabase_token(raw_token)
        if supabase_user and "id" in supabase_user:
            supabase_id = str(supabase_user["id"])
            email = supabase_user.get("email")
            user_metadata = supabase_user.get("user_metadata") or {}
            target_role = user_metadata.get("target_role") or "ML Engineer"
            username = user_metadata.get("username") or (email.split("@")[0] if email else f"user_{supabase_id[:8]}")

            # Check if user already exists by supabase_id
            res = await db.execute(select(models.User).filter(models.User.supabase_id == supabase_id))
            user = res.scalars().first()

            # Fallback check by email or username
            if not user and email:
                res_email = await db.execute(select(models.User).filter(models.User.email == email))
                user = res_email.scalars().first()
                if user and not user.supabase_id:
                    user.supabase_id = supabase_id
                    await db.commit()

            # If user still does not exist, provision new user and UserState
            if not user:
                # Ensure unique username
                u_check = await db.execute(select(models.User).filter(models.User.username == username))
                if u_check.scalars().first():
                    username = f"{username}_{supabase_id[:4]}"

                user = models.User(
                    supabase_id=supabase_id,
                    username=username,
                    email=email
                )
                db.add(user)
                await db.commit()
                await db.refresh(user)

                user_state = models.UserState(
                    user_id=user.id,
                    target_role=target_role,
                    current_topic="Machine Learning",
                    current_difficulty="beginner",
                    current_module="intro",
                    module_progress={"Machine Learning": {"intro": "active", "core": "locked", "summary": "locked"}},
                    fatigue=0.0,
                    created_at=datetime.utcnow().isoformat(),
                    updated_at=datetime.utcnow().isoformat()
                )
                db.add(user_state)

                activity = models.LearningActivity(
                    user_id=user.id,
                    activity_type="started_course",
                    title="Joined SkillPath AI",
                    description=f"Welcome to your personalized learning journey towards {target_role}!",
                    topic="Machine Learning",
                    created_at=datetime.utcnow().isoformat()
                )
                db.add(activity)
                await db.commit()
            else:
                # Ensure UserState exists for existing user
                st_res = await db.execute(select(models.UserState).filter(models.UserState.user_id == user.id))
                user_state = st_res.scalars().first()
                if not user_state:
                    user_state = models.UserState(
                        user_id=user.id,
                        target_role=target_role,
                        current_topic="Machine Learning",
                        current_difficulty="beginner",
                        current_module="intro",
                        module_progress={"Machine Learning": {"intro": "active", "core": "locked", "summary": "locked"}},
                        fatigue=0.0,
                        created_at=datetime.utcnow().isoformat(),
                        updated_at=datetime.utcnow().isoformat()
                    )
                    db.add(user_state)
                    await db.commit()

            return user

    # ── Path B: Check Session token in Redis / in-memory store ──
    user_id = await get_session(raw_token)
    if user_id:
        result = await db.execute(select(models.User).filter(models.User.id == user_id))
        user = result.scalars().first()
        if user:
            return user

    raise HTTPException(status_code=401, detail="Invalid or expired session. Please log in.")
