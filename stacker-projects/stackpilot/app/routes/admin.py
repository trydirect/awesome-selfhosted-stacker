from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.database import get_db
from app.knowledge import (
    add_document,
    add_website,
    count_documents,
    crawl_website,
    delete_document,
    delete_website,
    list_documents,
    list_websites,
)
from app.models import (
    CrawlRequest,
    DocumentIn,
    StatsResponse,
    WebsiteIn,
)
from app.rag import check_ollama_health, list_models, pull_model

router = APIRouter(prefix="/api/admin", tags=["admin"])


def _check_auth(request: Request) -> bool:
    from app.config import settings
    auth = request.cookies.get("sp_auth")
    return auth == settings.secret_key


@router.get("/stats", response_model=StatsResponse)
async def get_stats():
    db = await get_db()
    async with db.acquire() as conn:
        docs = await conn.fetchrow("SELECT count(*) as c FROM documents")
        convs = await conn.fetchrow("SELECT count(*) as c FROM conversations")
        sites = await conn.fetchrow("SELECT count(*) as c FROM websites")
        resolved = await conn.fetchrow("SELECT count(*) as c FROM conversations WHERE resolved = true")
        avg_msgs = await conn.fetchrow(
            "SELECT COALESCE(avg(jsonb_array_length(messages)), 0) as avg FROM conversations"
        )
    return StatsResponse(
        total_documents=docs["c"],
        total_conversations=convs["c"],
        total_websites=sites["c"],
        resolved_conversations=resolved["c"],
        avg_messages_per_conversation=round(float(avg_msgs["avg"]), 1),
    )


@router.get("/documents")
async def get_documents(offset: int = 0, limit: int = 50):
    docs = await list_documents(offset, limit)
    total = await count_documents()
    return {"documents": docs, "total": total}


@router.post("/documents")
async def create_document(doc: DocumentIn):
    doc_id = await add_document(doc.title, doc.content, doc.source, doc.metadata)
    return {"id": doc_id, "ok": True}


@router.delete("/documents/{doc_id}")
async def remove_document(doc_id: int):
    deleted = await delete_document(doc_id)
    return {"ok": deleted}


@router.get("/websites")
async def get_websites():
    sites = await list_websites()
    return {"websites": sites}


@router.post("/websites")
async def create_website(site: WebsiteIn):
    site_id = await add_website(site.domain, site.name, site.crawl_urls)
    return {"id": site_id, "ok": True}


@router.delete("/websites/{site_id}")
async def remove_website(site_id: int):
    deleted = await delete_website(site_id)
    return {"ok": deleted}


@router.post("/websites/crawl")
async def start_crawl(req: CrawlRequest):
    result = await crawl_website(req.url, req.max_pages, req.website_id)
    return result


@router.get("/conversations")
async def get_conversations(offset: int = 0, limit: int = 50):
    db = await get_db()
    async with db.acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM conversations ORDER BY id DESC LIMIT $1 OFFSET $2",
            limit, offset,
        )
    return {"conversations": [dict(r) for r in rows]}


@router.get("/ollama/status")
async def ollama_status():
    healthy = await check_ollama_health()
    models = await list_models() if healthy else []
    return {"healthy": healthy, "models": models}


@router.post("/ollama/pull")
async def ollama_pull_model(model: str):
    ok = await pull_model(model)
    return {"ok": ok}


@router.get("/dashboard", response_model=None)
async def dashboard():
    from pathlib import Path
    html_path = Path(__file__).parent.parent / "templates" / "dashboard.html"
    return HTMLResponse(content=html_path.read_text())


@router.post("/login")
async def login(request: Request, password: str):
    from app.config import settings
    from fastapi.responses import JSONResponse
    if password == settings.admin_password:
        resp = JSONResponse({"ok": True})
        resp.set_cookie("sp_auth", settings.secret_key, httponly=True, max_age=86400)
        return resp
    return JSONResponse({"ok": False, "error": "Invalid password"}, status_code=401)


@router.post("/logout")
async def logout():
    from fastapi.responses import JSONResponse
    resp = JSONResponse({"ok": True})
    resp.delete_cookie("sp_auth")
    return resp
