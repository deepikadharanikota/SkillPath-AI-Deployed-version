import os
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

import uuid
from sqlalchemy.pool import NullPool

raw_url = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@db:5432/skillpath"
).strip().strip("\"'").strip()

# Normalize PostgreSQL URL
if raw_url.startswith("postgres://"):
    raw_url = "postgresql+asyncpg://" + raw_url[len("postgres://"):]
elif raw_url.startswith("postgresql://") and not raw_url.startswith("postgresql+asyncpg://"):
    raw_url = "postgresql+asyncpg://" + raw_url[len("postgresql://"):]

connect_args = {}
is_remote = False

try:
    parsed = urlparse(raw_url)
    query_params = parse_qs(parsed.query)

    is_remote = parsed.hostname not in (
        "localhost",
        "127.0.0.1",
        "db",
        None
    )

    if "sslmode" in query_params or is_remote:
        query_params.pop("sslmode", None)
        connect_args["ssl"] = "require"

    # IMPORTANT:
    # Supabase/pgBouncer transaction pooling (e.g. port 6543) does not work
    # with asyncpg sequential statement names. Disabling statement caching and
    # providing globally unique statement names eliminates collisions completely.
    if is_remote:
        connect_args["statement_cache_size"] = 0
        connect_args["prepared_statement_cache_size"] = 0
        connect_args["prepared_statement_name_func"] = lambda: f"__asyncpg_{uuid.uuid4()}__"

    clean_query = urlencode(query_params, doseq=True)
    DATABASE_URL = urlunparse(
        parsed._replace(query=clean_query)
    )

except Exception:
    DATABASE_URL = raw_url


if is_remote:
    # Supabase connection pooler handles pooling: use NullPool to prevent connection retention
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,
        connect_args=connect_args,
        poolclass=NullPool,
        execution_options={"compiled_cache": None}
    )
else:
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