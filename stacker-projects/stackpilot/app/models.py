from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str
    timestamp: datetime | None = None


class ChatRequest(BaseModel):
    message: str
    session_id: str = ""
    visitor_id: str = ""
    website: str = ""


class ChatResponse(BaseModel):
    reply: str
    session_id: str
    sources: list[DocumentRef] = []
    confidence: float = 0.0


class DocumentRef(BaseModel):
    id: int
    title: str
    source: str
    score: float = 0.0


class DocumentIn(BaseModel):
    title: str = ""
    content: str
    source: str = ""
    metadata: dict[str, Any] = {}


class DocumentOut(BaseModel):
    id: int
    title: str
    source: str
    content: str
    chunk_index: int
    metadata: dict[str, Any] = {}
    created_at: datetime


class WebsiteIn(BaseModel):
    domain: str
    name: str = ""
    crawl_urls: list[str] = []


class WebsiteOut(BaseModel):
    id: int
    domain: str
    name: str
    crawl_urls: list[str]
    created_at: datetime


class ConversationOut(BaseModel):
    id: int
    session_id: str
    visitor_id: str
    website: str
    messages: list[ChatMessage]
    feedback: str
    resolved: bool
    created_at: datetime
    updated_at: datetime


class StatsResponse(BaseModel):
    total_documents: int
    total_conversations: int
    total_websites: int
    resolved_conversations: int
    avg_messages_per_conversation: float


class CrawlRequest(BaseModel):
    url: str
    max_pages: int = 50
    website_id: int | None = None


class FeedbackRequest(BaseModel):
    conversation_id: int
    feedback: str = Field(..., pattern="^(good|bad)$")


class ResolveRequest(BaseModel):
    conversation_id: int
    resolved: bool = True


ChatResponse.model_rebuild()
