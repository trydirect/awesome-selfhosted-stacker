from __future__ import annotations

import uuid
from datetime import datetime

import asyncpg
from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse

from app.database import get_db, get_redis
from app.models import ChatRequest, ChatResponse
from app.rag import escalate_to_n8n, generate_response

router = APIRouter(prefix="/api/widget", tags=["widget"])


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    db = await get_db()
    session_id = req.session_id or str(uuid.uuid4())
    async with db.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT messages FROM conversations WHERE session_id = $1 ORDER BY id DESC LIMIT 1",
            session_id,
        )
    history = list(row["messages"]) if row else []
    result = await generate_response(req.message, history)
    user_msg = {"role": "user", "content": req.message, "timestamp": datetime.utcnow().isoformat()}
    assistant_msg = {"role": "assistant", "content": result["reply"], "timestamp": datetime.utcnow().isoformat()}
    history.append(user_msg)
    history.append(assistant_msg)
    import json as _json
    messages_json = _json.dumps(history)
    async with db.acquire() as conn:
        existing = await conn.fetchrow(
            "SELECT id FROM conversations WHERE session_id = $1 ORDER BY id DESC LIMIT 1",
            session_id,
        )
        if existing:
            await conn.execute(
                "UPDATE conversations SET messages = $1::jsonb, updated_at = now() WHERE id = $2",
                messages_json, existing["id"],
            )
            conv_id = existing["id"]
        else:
            row = await conn.fetchrow(
                """INSERT INTO conversations (session_id, visitor_id, website, messages)
                   VALUES ($1, $2, $3, $4::jsonb) RETURNING id""",
                session_id, req.visitor_id, req.website, messages_json,
            )
            conv_id = row["id"]
    if result["confidence"] < 0.3:
        await escalate_to_n8n(conv_id, "low_confidence", history)
    return ChatResponse(
        reply=result["reply"],
        session_id=session_id,
        sources=result["sources"],
        confidence=result["confidence"],
    )


@router.get("/widget.js")
async def serve_widget_js(request: Request):
    base = str(request.base_url).rstrip("/")
    js = f"""
(function() {{
  var SP_HOST = "{base}";
  var SP_CONFIG = {{
    position: "bottom-right",
    theme: "light",
    title: "Support Assistant",
    subtitle: "Ask me anything"
  }};

  var container = document.createElement("div");
  container.id = "stackpilot-widget";
  document.body.appendChild(container);

  var style = document.createElement("style");
  style.textContent = `
    #sp-chat-launcher {{
      position: fixed; bottom: 20px; right: 20px; width: 60px; height: 60px;
      border-radius: 50%; background: #2563eb; color: white; border: none;
      cursor: pointer; box-shadow: 0 4px 12px rgba(0,0,0,0.15); z-index: 99999;
      font-size: 28px; display: flex; align-items: center; justify-content: center;
      transition: transform 0.2s;
    }}
    #sp-chat-launcher:hover {{ transform: scale(1.1); }}
    #sp-chat-window {{
      position: fixed; bottom: 90px; right: 20px; width: 380px; height: 520px;
      background: white; border-radius: 12px; box-shadow: 0 8px 30px rgba(0,0,0,0.12);
      display: none; flex-direction: column; z-index: 99999; overflow: hidden;
      font-family: -apple-system, BlinkMacSystemFont, sans-serif;
    }}
    #sp-chat-header {{
      background: #2563eb; color: white; padding: 16px; display: flex;
      justify-content: space-between; align-items: center;
    }}
    #sp-chat-header h3 {{ margin: 0; font-size: 16px; }}
    #sp-chat-messages {{
      flex: 1; overflow-y: auto; padding: 16px; display: flex;
      flex-direction: column; gap: 12px;
    }}
    .sp-msg {{ max-width: 85%; padding: 10px 14px; border-radius: 12px; font-size: 14px; line-height: 1.5; }}
    .sp-msg.user {{ align-self: flex-end; background: #2563eb; color: white; border-bottom-right-radius: 4px; }}
    .sp-msg.bot {{ align-self: flex-start; background: #f1f5f9; color: #1e293b; border-bottom-left-radius: 4px; }}
    #sp-chat-input-area {{ padding: 12px; border-top: 1px solid #e2e8f0; display: flex; gap: 8px; }}
    #sp-chat-input {{ flex: 1; padding: 10px; border: 1px solid #e2e8f0; border-radius: 8px; font-size: 14px; outline: none; }}
    #sp-chat-send {{ background: #2563eb; color: white; border: none; border-radius: 8px; padding: 10px 16px; cursor: pointer; font-size: 14px; }}
  `;
  document.head.appendChild(style);

  var sessionId = localStorage.getItem("sp_session_id") || (function() {{
    var id = "sp_" + Math.random().toString(36).substr(2, 9);
    localStorage.setItem("sp_session_id", id);
    return id;
  }})();

  container.innerHTML = '<button id="sp-chat-launcher">&#128172;</button>' +
    '<div id="sp-chat-window">' +
      '<div id="sp-chat-header"><h3>' + SP_CONFIG.title + '</h3><button id="sp-close" style="background:none;border:none;color:white;font-size:20px;cursor:pointer">&times;</button></div>' +
      '<div id="sp-chat-messages"><div class="sp-msg bot">' + SP_CONFIG.subtitle + '</div></div>' +
      '<div id="sp-chat-input-area"><input id="sp-chat-input" placeholder="Type your message..." /><button id="sp-chat-send">Send</button></div>' +
    '</div>';

  var launcher = document.getElementById("sp-chat-launcher");
  var window_ = document.getElementById("sp-chat-window");
  var close = document.getElementById("sp-close");
  var messages = document.getElementById("sp-chat-messages");
  var input = document.getElementById("sp-chat-input");
  var sendBtn = document.getElementById("sp-chat-send");

  launcher.addEventListener("click", function() {{
    window_.style.display = window_.style.display === "flex" ? "none" : "flex";
    if (window_.style.display === "flex") input.focus();
  }});
  close.addEventListener("click", function() {{ window_.style.display = "none"; }});

  function addMessage(text, role) {{
    var div = document.createElement("div");
    div.className = "sp-msg " + (role === "user" ? "user" : "bot");
    div.textContent = text;
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
  }}

  async function sendMessage() {{
    var text = input.value.trim();
    if (!text) return;
    addMessage(text, "user");
    input.value = "";
    sendBtn.disabled = true;
    try {{
      var resp = await fetch(SP_HOST + "/api/widget/chat", {{
        method: "POST",
        headers: {{ "Content-Type": "application/json" }},
        body: JSON.stringify({{ message: text, session_id: sessionId, website: window.location.hostname }})
      }});
      var data = await resp.json();
      addMessage(data.reply, "bot");
    }} catch(e) {{
      addMessage("Sorry, something went wrong. Please try again.", "bot");
    }}
    sendBtn.disabled = false;
    input.focus();
  }}

  sendBtn.addEventListener("click", sendMessage);
  input.addEventListener("keydown", function(e) {{ if (e.key === "Enter") sendMessage(); }});
}})();
"""
    return PlainTextResponse(js, media_type="application/javascript")


@router.post("/feedback")
async def feedback(conversation_id: int, feedback: str):
    db = await get_db()
    async with db.acquire() as conn:
        await conn.execute(
            "UPDATE conversations SET feedback = $1, updated_at = now() WHERE id = $2",
            feedback, conversation_id,
        )
    return {"ok": True}


@router.post("/resolve")
async def resolve(conversation_id: int, resolved: bool = True):
    db = await get_db()
    async with db.acquire() as conn:
        await conn.execute(
            "UPDATE conversations SET resolved = $1, updated_at = now() WHERE id = $2",
            resolved, conversation_id,
        )
    return {"ok": True}
