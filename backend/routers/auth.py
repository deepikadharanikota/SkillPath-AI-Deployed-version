import os
import uuid
import secrets
import urllib.parse
from typing import Optional
import httpx
from fastapi import APIRouter, Depends, Request, Header, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database import get_db
import models
from redis_client import set_session, redis_client
from auth_utils import get_current_user

router = APIRouter()

GITHUB_CLIENT_ID = (os.getenv("GITHUB_CLIENT_ID") or "").strip() or "mock_id"
GITHUB_CLIENT_SECRET = (os.getenv("GITHUB_CLIENT_SECRET") or "").strip() or "mock_secret"
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:8503")

GITHUB_AUTH_URL = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_USER_URL = "https://api.github.com/user"
GITHUB_EMAILS_URL = "https://api.github.com/user/emails"

@router.get("/login")
async def login(request: Request):
    if not GITHUB_CLIENT_ID or GITHUB_CLIENT_ID == "mock_id":
        # Mock auth flow for testing without real credentials
        return RedirectResponse(url="/auth/mock_callback")
    
    state = secrets.token_urlsafe(32)
    await redis_client.set(f"oauth_state:{state}", "1", ex=600)
    
    redirect_uri = str(request.url_for('auth_callback'))
    params = {
        "client_id": GITHUB_CLIENT_ID,
        "redirect_uri": redirect_uri,
        "scope": "read:user user:email",
        "state": state,
    }
    auth_url = f"{GITHUB_AUTH_URL}?{urllib.parse.urlencode(params)}"
    return RedirectResponse(url=auth_url)

@router.get("/callback")
async def auth_callback(
    request: Request,
    code: Optional[str] = None,
    state: Optional[str] = None,
    error: Optional[str] = None,
    error_description: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    if error:
        err_msg = error_description or error
        return RedirectResponse(url=f"{FRONTEND_URL}/login?error={urllib.parse.quote(err_msg)}")
    
    if not code:
        return RedirectResponse(url=f"{FRONTEND_URL}/login?error={urllib.parse.quote('Authorization code missing')}")
    
    if state:
        is_valid = await redis_client.get(f"oauth_state:{state}")
        if not is_valid:
            return RedirectResponse(url=f"{FRONTEND_URL}/login?error={urllib.parse.quote('Invalid or expired OAuth state')}")
        await redis_client.delete(f"oauth_state:{state}")
    
    try:
        redirect_uri = str(request.url_for('auth_callback'))
        async with httpx.AsyncClient() as client:
            token_resp = await client.post(
                GITHUB_TOKEN_URL,
                headers={"Accept": "application/json"},
                data={
                    "client_id": GITHUB_CLIENT_ID,
                    "client_secret": GITHUB_CLIENT_SECRET,
                    "code": code,
                    "redirect_uri": redirect_uri,
                }
            )
            token_data = token_resp.json()
            access_token = token_data.get("access_token")
            if not access_token:
                err = token_data.get("error_description", token_data.get("error", "Failed to retrieve access token from GitHub"))
                return RedirectResponse(url=f"{FRONTEND_URL}/login?error={urllib.parse.quote(err)}")
            
            user_resp = await client.get(
                GITHUB_USER_URL,
                headers={"Authorization": f"Bearer {access_token}", "Accept": "application/json"}
            )
            if user_resp.status_code != 200:
                return RedirectResponse(url=f"{FRONTEND_URL}/login?error={urllib.parse.quote('Failed to fetch user profile from GitHub')}")
            user_info = user_resp.json()
            
            # Fetch emails if email is not visible in public profile
            if not user_info.get("email"):
                emails_resp = await client.get(
                    GITHUB_EMAILS_URL,
                    headers={"Authorization": f"Bearer {access_token}", "Accept": "application/json"}
                )
                if emails_resp.status_code == 200:
                    for em in emails_resp.json():
                        if em.get("primary") and em.get("verified"):
                            user_info["email"] = em.get("email")
                            break
                        elif em.get("primary"):
                            user_info["email"] = em.get("email")
    except Exception as e:
        return RedirectResponse(url=f"{FRONTEND_URL}/login?error={urllib.parse.quote(str(e))}")
    
    return await _process_user(user_info, db)

@router.get("/mock_callback")
async def mock_callback(db: AsyncSession = Depends(get_db)):
    user_info = {
        "id": "mock_github_123",
        "login": "mock_user",
        "email": "mock@example.com"
    }
    return await _process_user(user_info, db)

async def _process_user(user_info: dict, db: AsyncSession):
    github_id = str(user_info.get("id"))
    username = user_info.get("login")
    email = user_info.get("email")
    
    # Check if user exists by github_id
    result = await db.execute(select(models.User).filter(models.User.github_id == github_id))
    user = result.scalars().first()
    
    # Fallback check by username if not found by github_id
    if not user and username:
        u_res = await db.execute(select(models.User).filter(models.User.username == username))
        existing_user = u_res.scalars().first()
        if existing_user and not existing_user.github_id:
            existing_user.github_id = github_id
            if email and not existing_user.email:
                existing_user.email = email
            await db.commit()
            user = existing_user

    if not user:
        user = models.User(github_id=github_id, username=username, email=email)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        # Initialize User State
        user_state = models.UserState(
            user_id=user.id,
            target_role="ML Engineer",
            current_topic="Machine Learning",
            current_difficulty="beginner",
            current_module="intro",
            module_progress={"Machine Learning": {"intro": "active", "core": "locked", "summary": "locked"}},
            fatigue=0.0
        )
        db.add(user_state)

        from datetime import datetime
        act = models.LearningActivity(
            user_id=user.id,
            activity_type="started_course",
            title="Joined via GitHub",
            description="Welcome to your personalized learning journey with SkillPath AI!",
            topic="Machine Learning",
            created_at=datetime.utcnow().isoformat()
        )
        db.add(act)
        await db.commit()
    else:
        if email and user.email != email:
            user.email = email
            await db.commit()
            
        # Ensure user_state exists
        st_res = await db.execute(select(models.UserState).filter(models.UserState.user_id == user.id))
        user_state = st_res.scalars().first()
        if not user_state:
            user_state = models.UserState(
                user_id=user.id,
                target_role="ML Engineer",
                current_topic="Machine Learning",
                current_difficulty="beginner",
                current_module="intro",
                module_progress={"Machine Learning": {"intro": "active", "core": "locked", "summary": "locked"}},
                fatigue=0.0
            )
            db.add(user_state)
            await db.commit()
        
    session_id = str(uuid.uuid4())
    await set_session(session_id, user.id)
    
    # Redirect to frontend with token
    return RedirectResponse(url=f"{FRONTEND_URL}/?token={session_id}")

from pydantic import BaseModel
import hashlib

def hash_password(password: str) -> str:
    salt = os.urandom(16).hex()
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), bytes.fromhex(salt), 100000)
    return f"{salt}:{key.hex()}"

def verify_password(password: str, hashed: str) -> bool:
    try:
        salt, key_hex = hashed.split(":")
        new_key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), bytes.fromhex(salt), 100000)
        return secrets.compare_digest(new_key.hex(), key_hex)
    except Exception:
        return False

class RegisterPayload(BaseModel):
    username: str
    email: Optional[str] = None
    password: str
    target_role: Optional[str] = "ML Engineer"

class LoginPayload(BaseModel):
    username: str
    password: str

@router.post("/register")
async def register(payload: RegisterPayload, db: AsyncSession = Depends(get_db)):
    """Creates a new user account with credentials."""
    uname = payload.username.strip()
    if not uname or not payload.password:
        raise HTTPException(status_code=400, detail="Username and password are required")

    # Check if user already exists
    res = await db.execute(select(models.User).filter(models.User.username == uname))
    if res.scalars().first():
        raise HTTPException(status_code=400, detail="Username is already registered. Please log in.")

    # Hash password
    pw_hash = hash_password(payload.password)

    user = models.User(
        username=uname,
        email=payload.email.strip() if payload.email else f"{uname}@skillpath.local",
        password_hash=pw_hash
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # Initialize User State
    target_role = payload.target_role or "ML Engineer"
    user_state = models.UserState(
        user_id=user.id,
        target_role=target_role,
        current_topic="Machine Learning",
        current_difficulty="beginner",
        current_module="intro",
        module_progress={"Machine Learning": {"intro": "active", "core": "locked", "summary": "locked"}},
        fatigue=0.0
    )
    db.add(user_state)

    # Log welcome activity
    from datetime import datetime
    act = models.LearningActivity(
        user_id=user.id,
        activity_type="started_course",
        title="Created SkillPath AI Account",
        description=f"Welcome to your personalized learning journey towards {target_role}!",
        topic="Machine Learning",
        created_at=datetime.utcnow().isoformat()
    )
    db.add(act)

    await db.commit()

    # Create session
    session_id = str(uuid.uuid4())
    await set_session(session_id, user.id)

    return {
        "success": True,
        "token": session_id,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "target_role": target_role
        }
    }

@router.post("/local-login")
async def local_login(payload: LoginPayload, db: AsyncSession = Depends(get_db)):
    """Direct username/password login."""
    uname = payload.username.strip()
    res = await db.execute(select(models.User).filter(models.User.username == uname))
    user = res.scalars().first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # Verify password if hashed
    if user.password_hash:
        if not verify_password(payload.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid username or password")

    # Generate session
    session_id = str(uuid.uuid4())
    await set_session(session_id, user.id)

    # Fetch user state
    st_res = await db.execute(select(models.UserState).filter(models.UserState.user_id == user.id))
    user_state = st_res.scalars().first()

    return {
        "success": True,
        "token": session_id,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "target_role": user_state.target_role if user_state else "ML Engineer"
        }
    }

@router.get("/me")
async def get_current_user_profile(
    token: str = Header(...),
    db: AsyncSession = Depends(get_db)
):
    """Returns current logged-in user profile and settings."""
    user_id = await redis_client.get(f"session:{token}")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    user_res = await db.execute(select(models.User).filter(models.User.id == int(user_id)))
    user = user_res.scalars().first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    st_res = await db.execute(select(models.UserState).filter(models.UserState.user_id == user.id))
    state = st_res.scalars().first()

    return {
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "target_role": state.target_role if state else "ML Engineer",
            "has_resume": bool(state and state.resume_filename),
            "resume_filename": state.resume_filename if state else None,
            "current_topic": state.current_topic if state else "Machine Learning",
            "current_difficulty": state.current_difficulty if state else "beginner",
            "total_hours": state.total_learning_hours if state else 0,
            "streak": state.current_streak if state else 0,
            "dsa_language": getattr(state, "dsa_language", "Python") or "Python",
            "dsaLanguage": getattr(state, "dsa_language", "Python") or "Python",
            "dsa_lang_code": ("cpp" if getattr(state, "dsa_language", "").lower() in ["c++", "cpp"] else getattr(state, "dsa_language", "python").lower()) if state else "python",
            "initial_performance_category": getattr(state, "initial_performance_category", None),
            "current_ability": getattr(state, "current_ability", 0.5) if state else 0.5
        }
    }

@router.post("/logout")
async def logout(token: str = Header(...)):
    """Logs out by clearing session token from Redis."""
    from redis_client import delete_session
    await delete_session(token)
    return {"success": True, "message": "Logged out successfully"}

