"""Integration tests for API routes — uses httpx AsyncClient with test app."""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch, MagicMock

from app.main import app


class _AsyncCtxManager:
    """Mimics asyncpg pool.acquire() — returns an async context manager directly."""
    def __init__(self, conn):
        self._conn = conn
    async def __aenter__(self):
        return self._conn
    async def __aexit__(self, *args):
        return False


def _make_mock_pool(mock_conn):
    mock_pool = MagicMock()
    mock_pool.acquire.return_value = _AsyncCtxManager(mock_conn)
    return mock_pool


class TestHealthEndpoint:
    """BDD: Health check endpoint"""

    @pytest.mark.asyncio
    @patch("app.rag.check_ollama_health")
    async def test_health_returns_ok(self, mock_health):
        mock_health.return_value = True
        from httpx import AsyncClient, ASGITransport
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["ollama"] is True


class TestAdminStats:
    """BDD: Admin statistics endpoint"""

    @pytest.mark.asyncio
    @patch("app.routes.admin.get_db")
    async def test_stats_returns_structure(self, mock_db):
        mock_conn = AsyncMock()
        mock_conn.fetchrow = AsyncMock(side_effect=[
            {"c": 10},
            {"c": 5},
            {"c": 2},
            {"c": 3},
            {"avg": 2.5},
        ])
        mock_db.return_value = _make_mock_pool(mock_conn)

        from httpx import AsyncClient, ASGITransport
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/api/admin/stats")
        assert resp.status_code == 200
        data = resp.json()
        assert "total_documents" in data
        assert "total_conversations" in data
        assert "total_websites" in data
        assert "resolved_conversations" in data


class TestAdminDashboard:
    """BDD: Admin dashboard serves HTML"""

    @pytest.mark.asyncio
    async def test_dashboard_serves_html(self):
        from httpx import AsyncClient, ASGITransport
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/api/admin/dashboard")
        assert resp.status_code == 200
        assert "StackPilot" in resp.text

    @pytest.mark.asyncio
    async def test_root_serves_html(self):
        from httpx import AsyncClient, ASGITransport
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/")
        assert resp.status_code == 200
        assert "StackPilot" in resp.text


class TestWidgetEndpoint:
    """BDD: Chat widget JavaScript serving"""

    @pytest.mark.asyncio
    async def test_widget_js_serves_javascript(self):
        from httpx import AsyncClient, ASGITransport
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/api/widget/widget.js")
        assert resp.status_code == 200
        assert "stackpilot" in resp.text.lower()

    @pytest.mark.asyncio
    @patch("app.routes.widget.generate_response")
    @patch("app.routes.widget.get_db")
    async def test_chat_endpoint_returns_response(self, mock_db, mock_gen):
        mock_gen.return_value = {
            "reply": "Hello! How can I help?",
            "sources": [],
            "confidence": 0.9,
        }
        mock_conn = AsyncMock()
        # First call: SELECT to check existing conversation → None (new session)
        # Second call: INSERT conversation → return id
        mock_conn.fetchrow = AsyncMock(side_effect=[
            None,  # SELECT existing conversation
            {"id": 1},  # INSERT returning id
        ])
        mock_db.return_value = _make_mock_pool(mock_conn)

        from httpx import AsyncClient, ASGITransport
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post("/api/widget/chat", json={
                "message": "Hello",
                "session_id": "test-123",
                "website": "test.com",
            })
        assert resp.status_code == 200
        data = resp.json()
        assert "reply" in data
        assert "session_id" in data
        assert "confidence" in data
