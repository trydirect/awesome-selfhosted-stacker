import asyncpg
import redis.asyncio as aioredis
from pgvector.asyncpg import register_vector

from app.config import settings

_pool: asyncpg.Pool | None = None
_redis: aioredis.Redis | None = None


async def init_db() -> asyncpg.Pool:
    global _pool
    _pool = await asyncpg.create_pool(settings.database_url, min_size=2, max_size=10)
    async with _pool.acquire() as conn:
        await register_vector(conn)
        await conn.execute("""
            CREATE EXTENSION IF NOT EXISTS vector;
            CREATE EXTENSION IF NOT EXISTS pg_trgm;
        """)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id          SERIAL PRIMARY KEY,
                source      TEXT NOT NULL DEFAULT '',
                title       TEXT NOT NULL DEFAULT '',
                content     TEXT NOT NULL,
                chunk_index INTEGER NOT NULL DEFAULT 0,
                metadata    JSONB DEFAULT '{}',
                created_at  TIMESTAMPTZ DEFAULT now()
            );
        """)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS document_embeddings (
                id          SERIAL PRIMARY KEY,
                document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
                embedding   vector(768),
                created_at  TIMESTAMPTZ DEFAULT now()
            );
        """)
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_doc_emb_vector
            ON document_embeddings USING ivfflat (embedding vector_cosine_ops)
            WITH (lists = 100);
        """)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id          SERIAL PRIMARY KEY,
                session_id  TEXT NOT NULL,
                visitor_id  TEXT NOT NULL DEFAULT '',
                website     TEXT NOT NULL DEFAULT '',
                messages    JSONB DEFAULT '[]',
                feedback    TEXT DEFAULT '',
                resolved    BOOLEAN DEFAULT false,
                created_at  TIMESTAMPTZ DEFAULT now(),
                updated_at  TIMESTAMPTZ DEFAULT now()
            );
        """)
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_conv_session
            ON conversations(session_id);
        """)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS websites (
                id          SERIAL PRIMARY KEY,
                domain      TEXT UNIQUE NOT NULL,
                name        TEXT NOT NULL DEFAULT '',
                crawl_urls  TEXT[] DEFAULT '{}',
                settings    JSONB DEFAULT '{}',
                created_at  TIMESTAMPTZ DEFAULT now()
            );
        """)
    return _pool


async def get_db() -> asyncpg.Pool:
    assert _pool is not None, "Database not initialized"
    return _pool


def get_redis() -> aioredis.Redis:
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(settings.redis_url, decode_responses=True)
    return _redis


async def close_db():
    global _pool, _redis
    if _pool:
        await _pool.close()
    if _redis:
        await _redis.close()
