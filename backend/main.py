from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from database import engine, Base
import models
import os
from routers import auth, quiz, learning, dashboard, resume
from contextlib import asynccontextmanager
from sqlalchemy import text

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            migrations = [
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS supabase_id VARCHAR;",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS password_hash VARCHAR;",
                "ALTER TABLE user_states ADD COLUMN IF NOT EXISTS resume_filename VARCHAR;",
                "ALTER TABLE user_states ADD COLUMN IF NOT EXISTS resume_uploaded_at VARCHAR;",
                "ALTER TABLE user_states ADD COLUMN IF NOT EXISTS resume_file_path VARCHAR;",
                "ALTER TABLE user_states ADD COLUMN IF NOT EXISTS resume_text TEXT;",
                "ALTER TABLE user_states ADD COLUMN IF NOT EXISTS extracted_skills_categorized JSON;",
                "ALTER TABLE user_states ADD COLUMN IF NOT EXISTS video_progress JSON DEFAULT '{}'::json;",
                "ALTER TABLE user_states ADD COLUMN IF NOT EXISTS topic_ability JSON DEFAULT '{}'::json;",
                "ALTER TABLE user_states ADD COLUMN IF NOT EXISTS last_video_id VARCHAR;",
                "ALTER TABLE user_states ADD COLUMN IF NOT EXISTS last_video_title VARCHAR;",
                "ALTER TABLE user_states ADD COLUMN IF NOT EXISTS last_video_position_seconds FLOAT DEFAULT 0.0;",
                "ALTER TABLE user_states ADD COLUMN IF NOT EXISTS last_accessed_at VARCHAR;",
                "ALTER TABLE quiz_history ADD COLUMN IF NOT EXISTS quiz_id VARCHAR;",
                "ALTER TABLE quiz_history ADD COLUMN IF NOT EXISTS questions JSON;",
                "ALTER TABLE quiz_history ADD COLUMN IF NOT EXISTS user_answers JSON;",
                "ALTER TABLE quiz_history ADD COLUMN IF NOT EXISTS correct_answers JSON;",
                "ALTER TABLE quiz_history ADD COLUMN IF NOT EXISTS score INTEGER DEFAULT 0;",
                "ALTER TABLE quiz_history ADD COLUMN IF NOT EXISTS total_questions INTEGER DEFAULT 0;",
                "ALTER TABLE quiz_history ADD COLUMN IF NOT EXISTS percentage FLOAT DEFAULT 0.0;",
                "ALTER TABLE quiz_history ADD COLUMN IF NOT EXISTS unanswered INTEGER DEFAULT 0;",
                "ALTER TABLE quiz_history ADD COLUMN IF NOT EXISTS completed_at VARCHAR;",
                "ALTER TABLE user_states ADD COLUMN IF NOT EXISTS dsa_language VARCHAR DEFAULT 'Python';",
                "ALTER TABLE user_states ADD COLUMN IF NOT EXISTS initial_performance_category VARCHAR;",
                "ALTER TABLE user_states ADD COLUMN IF NOT EXISTS current_ability FLOAT DEFAULT 0.5;",
                "ALTER TABLE user_states ADD COLUMN IF NOT EXISTS created_at VARCHAR;",
                "ALTER TABLE user_states ADD COLUMN IF NOT EXISTS updated_at VARCHAR;",
                "CREATE INDEX IF NOT EXISTS ix_users_supabase_id ON users (supabase_id);",
                "CREATE INDEX IF NOT EXISTS ix_quiz_history_user_id ON quiz_history (user_id);",
                "CREATE INDEX IF NOT EXISTS ix_quiz_history_topic ON quiz_history (topic);",
                "CREATE INDEX IF NOT EXISTS ix_learning_activities_user_id ON learning_activities (user_id);",
                "CREATE INDEX IF NOT EXISTS ix_learning_activities_created_at ON learning_activities (created_at);",
                "CREATE INDEX IF NOT EXISTS ix_user_states_user_id ON user_states (user_id);",
            ]
            for stmt in migrations:
                try:
                    await conn.execute(text(stmt))
                except Exception as err:
                    print(f"Migration note: {err}")
    except Exception as db_err:
        print(f"[Warning] Database initialization deferred: {db_err}")
    yield

app = FastAPI(title="SkillPath AI Backend", lifespan=lifespan)

# Configurable CORS handling
default_origins = [
    "http://localhost:8503",
    "http://127.0.0.1:8503",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

env_origins = os.getenv("ALLOWED_ORIGINS", "")
frontend_url = os.getenv("FRONTEND_URL", "")

allowed_origins = list(default_origins)
if env_origins:
    for origin in env_origins.split(","):
        o = origin.strip()
        if o and o not in allowed_origins:
            allowed_origins.append(o)
if frontend_url and frontend_url not in allowed_origins:
    allowed_origins.append(frontend_url.strip())

# Allow all vercel.app domains by default for flexible deployments
allow_origin_regex = os.getenv("ALLOW_ORIGIN_REGEX", r"https:\/\/.*\.vercel\.app")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=allow_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY", "supersecretkey_change_me"))
from starlette.responses import JSONResponse

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    import traceback
    traceback.print_exc()
    origin = request.headers.get("origin", "*")
    headers = {
        "Access-Control-Allow-Origin": origin,
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Allow-Methods": "*",
        "Access-Control-Allow-Headers": "*",
    }
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "error_type": type(exc).__name__},
        headers=headers
    )

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(resume.router, prefix="/resume", tags=["resume"])
app.include_router(quiz.router, prefix="/quiz", tags=["quiz"])
app.include_router(learning.router, prefix="/learning", tags=["learning"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])

from data import ROLES
from roles_config import ROLES_REGISTRY

@app.get("/")
def read_root():
    return {"status": "ok"}

@app.get("/health")
async def health_check():
    """Production health check endpoint for Render with database verification."""
    db_status = "ok"
    db_error = None
    try:
        from database import engine
        from sqlalchemy import text
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception as e:
        db_status = "error"
        db_error = str(e)
    
    return {
        "status": "ok",
        "version": "1.0.2",
        "database": db_status,
        "database_error": db_error
    }

@app.get("/roles")
def get_roles():
    return {
        "roles": ROLES,
        "roles_detail": ROLES_REGISTRY
    }
