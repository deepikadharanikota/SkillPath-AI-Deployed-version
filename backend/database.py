import os
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

raw_url = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@db:5432/skillpath").strip()

# 1. Normalize connection scheme to postgresql+asyncpg://
if raw_url.startswith("postgres://"):
    raw_url = "postgresql+asyncpg://" + raw_url[len("postgres://"):]
elif raw_url.startswith("postgresql://") and not raw_url.startswith("postgresql+asyncpg://"):
    raw_url = "postgresql+asyncpg://" + raw_url[len("postgresql://"):]

# 2. Parse query parameters and configure SSL for asyncpg
connect_args = {}
try:
    parsed = urlparse(raw_url)
    query_params = parse_qs(parsed.query)

    # Supabase and cloud PostgreSQL databases require SSL.
    # asyncpg does not accept ?sslmode=... in query parameters, so we extract it into connect_args.
    is_remote = parsed.hostname not in ("localhost", "127.0.0.1", "db", None)
    if "sslmode" in query_params or is_remote:
        query_params.pop("sslmode", None)
        connect_args["ssl"] = "require"

    clean_query = urlencode(query_params, doseq=True)
    DATABASE_URL = urlunparse(parsed._replace(query=clean_query))
except Exception:
    DATABASE_URL = raw_url

# Production-safe connection pool with pre-ping and recycling
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    connect_args=connect_args,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=300
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

async def get_db():
    async with SessionLocal() as session:
        yield session
