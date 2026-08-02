from __future__ import annotations

from fastapi import APIRouter

from app.database import get_db

router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])


@router.post("/n8n")
async def n8n_webhook(payload: dict):
    event = payload.get("event", "")
    if event == "conversation.resolved":
        conv_id = payload.get("conversation_id")
        if conv_id:
            db = await get_db()
            async with db.acquire() as conn:
                await conn.execute(
                    "UPDATE conversations SET resolved = true, updated_at = now() WHERE id = $1",
                    conv_id,
                )
    elif event == "conversation.escalated":
        conv_id = payload.get("conversation_id")
        reason = payload.get("reason", "")
        if conv_id:
            db = await get_db()
            async with db.acquire() as conn:
                await conn.execute(
                    """UPDATE conversations
                       SET messages = messages || '[{{"role":"system","content":"Escalated: {reason}"}}]'::jsonb,
                           updated_at = now()
                       WHERE id = $1""",
                    conv_id,
                )
    return {"ok": True}


@router.post("/ingest")
async def ingest_webhook(payload: dict):
    title = payload.get("title", "")
    content = payload.get("content", "")
    source = payload.get("source", "")
    if not content:
        return {"ok": False, "error": "content is required"}
    from app.knowledge import add_document
    doc_id = await add_document(title, content, source)
    return {"ok": True, "document_id": doc_id}
