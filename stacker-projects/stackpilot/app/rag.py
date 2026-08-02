from __future__ import annotations

import httpx

from app.config import settings
from app.knowledge import search_similar


SYSTEM_PROMPT = """You are a helpful website support assistant. You answer questions based on the knowledge base provided below.
Rules:
- Answer based ONLY on the provided context when available.
- If the context does not contain enough information, say so honestly.
- Be concise, friendly, and professional.
- Do not make up information.
- Format responses in clean markdown when helpful.

KNOWLEDGE BASE CONTEXT:
{context}
"""


def build_context(results: list[dict]) -> str:
    if not results:
        return "No relevant knowledge base entries found."
    parts = []
    for i, r in enumerate(results, 1):
        source = r.get("source", "unknown")
        title = r.get("title", "")
        content = r.get("content", "")
        score = r.get("score", 0)
        parts.append(f"[Source {i}: {title or source}] (relevance: {score:.2f})\n{content}")
    return "\n\n---\n\n".join(parts)


async def generate_response(message: str, history: list[dict] | None = None) -> dict:
    results = await search_similar(message, limit=5)
    context = build_context(results)
    system_msg = SYSTEM_PROMPT.format(context=context)
    messages = [{"role": "system", "content": system_msg}]
    if history:
        for msg in history[-6:]:
            messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})
    messages.append({"role": "user", "content": message})
    async with httpx.AsyncClient(timeout=300) as client:
        resp = await client.post(
            f"{settings.ollama_base_url}/api/chat",
            json={
                "model": settings.ollama_model,
                "messages": messages,
                "stream": False,
            },
        )
        resp.raise_for_status()
        data = resp.json()
    reply = data.get("message", {}).get("content", "I could not generate a response.")
    sources = [
        {"id": r["id"], "title": r.get("title", ""), "source": r.get("source", ""), "score": r.get("score", 0)}
        for r in results[:3]
    ]
    confidence = results[0]["score"] if results else 0.0
    return {"reply": reply, "sources": sources, "confidence": confidence}


async def check_ollama_health() -> bool:
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(f"{settings.ollama_base_url}/api/tags")
            return resp.status_code == 200
    except Exception:
        return False


async def pull_model(model: str) -> bool:
    try:
        async with httpx.AsyncClient(timeout=600) as client:
            resp = await client.post(
                f"{settings.ollama_base_url}/api/pull",
                json={"name": model},
            )
            return resp.status_code == 200
    except Exception:
        return False


async def list_models() -> list[str]:
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(f"{settings.ollama_base_url}/api/tags")
            resp.raise_for_status()
            models = resp.json().get("models", [])
            return [m["name"] for m in models]
    except Exception:
        return []


async def escalate_to_n8n(conversation_id: int, reason: str, messages: list[dict]) -> bool:
    if not settings.n8n_webhook_url:
        return False
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                settings.n8n_webhook_url,
                json={
                    "event": "escalation",
                    "conversation_id": conversation_id,
                    "reason": reason,
                    "messages": messages,
                },
            )
            return resp.status_code < 400
    except Exception:
        return False
