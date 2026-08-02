from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.database import close_db, init_db
from app.routes import admin, webhooks, widget


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_db()


app = FastAPI(
    title="StackPilot",
    description="Self-Hosted AI Website Support Assistant",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(widget.router)
app.include_router(admin.router)
app.include_router(webhooks.router)


@app.get("/", response_class=HTMLResponse)
async def root():
    return HTMLResponse(
        content="""<!DOCTYPE html>
<html><head><title>StackPilot</title>
<style>body{font-family:sans-serif;display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0;background:#f8fafc}
.c{text-align:center}.c h1{font-size:48px;color:#2563eb;margin-bottom:8px}.c p{color:#64748b;font-size:18px}
.c a{display:inline-block;margin-top:24px;padding:12px 24px;background:#2563eb;color:white;text-decoration:none;border-radius:8px}
.c a:hover{background:#1d4ed8}</style></head>
<body><div class="c"><h1>StackPilot</h1><p>Self-Hosted AI Website Support Assistant</p>
<a href="/api/admin/dashboard">Open Dashboard</a></div></body></html>"""
    )


@app.get("/health")
async def health():
    from app.rag import check_ollama_health
    ollama_ok = await check_ollama_health()
    return {"status": "ok", "ollama": ollama_ok}
