from __future__ import annotations

import hashlib
import re
from typing import Any

import httpx
from pgvector.asyncpg import Vector, register_vector

from app.config import settings
from app.database import get_db, get_redis

CHUNK_SIZE = 500
CHUNK_OVERLAP = 100


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    text = re.sub(r"\s+", " ", text.strip())
    if len(text) <= chunk_size:
        return [text] if text else []
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        if chunk.strip():
            chunks.append(chunk.strip())
        start += chunk_size - overlap
    return chunks


async def embed_text(text: str) -> list[float]:
    async with httpx.AsyncClient(timeout=120) as client:
        resp = await client.post(
            f"{settings.ollama_base_url}/api/embeddings",
            json={"model": settings.ollama_embed_model, "prompt": text},
        )
        resp.raise_for_status()
        return resp.json()["embedding"]


async def embed_batch(texts: list[str]) -> list[list[float]]:
    embeddings = []
    for text in texts:
        emb = await embed_text(text)
        embeddings.append(emb)
    return embeddings


async def add_document(title: str, content: str, source: str = "", metadata: dict[str, Any] | None = None) -> int:
    import json
    db = await get_db()
    chunks = chunk_text(content)
    if not chunks:
        return -1
    embeddings = await embed_batch(chunks)
    doc_id = -1
    meta_json = json.dumps(metadata or {})
    async with db.acquire() as conn:
        await register_vector(conn)
        for i, (chunk, emb) in enumerate(zip(chunks, embeddings)):
            row = await conn.fetchrow(
                """INSERT INTO documents (source, title, content, chunk_index, metadata)
                   VALUES ($1, $2, $3, $4, $5::jsonb) RETURNING id""",
                source, title, chunk, i, meta_json,
            )
            if doc_id == -1:
                doc_id = row["id"]
            await conn.execute(
                """INSERT INTO document_embeddings (document_id, embedding)
                   VALUES ($1, $2)""",
                row["id"], Vector(emb),
            )
    return doc_id


async def search_similar(query: str, limit: int = 5) -> list[dict[str, Any]]:
    db = await get_db()
    query_emb = await embed_text(query)
    cache = get_redis()
    cache_key = f"search:{hashlib.md5(query.encode()).hexdigest()}:{limit}"
    cached = await cache.get(cache_key)
    if cached:
        import json
        return json.loads(cached)
    async with db.acquire() as conn:
        await register_vector(conn)
        rows = await conn.fetch(
            """SELECT d.id, d.title, d.source, d.content, d.metadata,
                      1 - (de.embedding <=> $1::vector) AS score
               FROM document_embeddings de
               JOIN documents d ON d.id = de.document_id
               ORDER BY de.embedding <=> $1::vector
               LIMIT $2""",
            Vector(query_emb), limit,
        )
    results = [dict(r) for r in rows]
    import json
    await cache.setex(cache_key, 300, json.dumps(results, default=str))
    return results


async def get_document(doc_id: int) -> dict[str, Any] | None:
    db = await get_db()
    async with db.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM documents WHERE id = $1", doc_id)
    return dict(row) if row else None


async def delete_document(doc_id: int) -> bool:
    db = await get_db()
    async with db.acquire() as conn:
        result = await conn.execute("DELETE FROM documents WHERE id = $1", doc_id)
    return result == "DELETE 1"


async def list_documents(offset: int = 0, limit: int = 50) -> list[dict[str, Any]]:
    db = await get_db()
    async with db.acquire() as conn:
        rows = await conn.fetch(
            "SELECT id, source, title, chunk_index, left(content, 200) as preview, created_at "
            "FROM documents ORDER BY id LIMIT $1 OFFSET $2",
            limit, offset,
        )
    return [dict(r) for r in rows]


async def count_documents() -> int:
    db = await get_db()
    async with db.acquire() as conn:
        row = await conn.fetchrow("SELECT count(*) as cnt FROM documents")
    return row["cnt"]


async def crawl_website(url: str, max_pages: int = 50, website_id: int | None = None) -> dict[str, Any]:
    import logging
    logger = logging.getLogger("stackpilot.crawl")
    visited: set[str] = set()
    queue = [url]
    pages_crawled = 0
    docs_added = 0
    from urllib.parse import urljoin, urlparse
    base_domain = urlparse(url).netloc
    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        while queue and pages_crawled < max_pages:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)
            try:
                resp = await client.get(current, headers={"User-Agent": "StackPilot/1.0"})
                if "text/html" not in resp.headers.get("content-type", ""):
                    logger.info("Skipping non-HTML: %s", current)
                    continue
                pages_crawled += 1
                html = resp.text
                text = _extract_text(html)
                title = _extract_title(html)
                logger.info("Crawled %s: title=%r, text_len=%d", current, title, len(text))
                if len(text.strip()) >= 50:
                    doc_id = await add_document(title=title, content=text, source=current)
                    if doc_id > 0:
                        docs_added += 1
                        logger.info("Added doc %d from %s", doc_id, current)
                else:
                    logger.warning("Text too short (%d chars) from %s", len(text), current)
                links = _extract_links(html, current)
                for link in links:
                    parsed = urlparse(link)
                    if parsed.netloc == base_domain and link not in visited:
                        queue.append(link)
            except Exception as e:
                logger.error("Failed to crawl %s: %s", current, e)
                continue
    return {"pages_crawled": pages_crawled, "documents_added": docs_added, "urls_visited": len(visited)}


def _extract_text(html: str) -> str:
    html = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r"<style[^>]*>.*?</style>", "", html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r"<[^>]+>", " ", html)
    html = re.sub(r"\s+", " ", html)
    return html.strip()


def _extract_title(html: str) -> str:
    m = re.search(r"<title[^>]*>(.*?)</title>", html, re.DOTALL | re.IGNORECASE)
    return m.group(1).strip() if m else ""


def _extract_links(html: str, base_url: str) -> list[str]:
    from urllib.parse import urljoin
    links = re.findall(r'href=["\']([^"\']+)["\']', html, re.IGNORECASE)
    return [urljoin(base_url, link) for link in links if link.startswith(("http", "/"))]


async def add_website(domain: str, name: str = "", crawl_urls: list[str] | None = None) -> int:
    db = await get_db()
    async with db.acquire() as conn:
        row = await conn.fetchrow(
            """INSERT INTO websites (domain, name, crawl_urls)
               VALUES ($1, $2, $3) RETURNING id""",
            domain, name, crawl_urls or [],
        )
    return row["id"]


async def list_websites() -> list[dict[str, Any]]:
    db = await get_db()
    async with db.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM websites ORDER BY id")
    return [dict(r) for r in rows]


async def delete_website(website_id: int) -> bool:
    db = await get_db()
    async with db.acquire() as conn:
        result = await conn.execute("DELETE FROM websites WHERE id = $1", website_id)
    return result == "DELETE 1"
