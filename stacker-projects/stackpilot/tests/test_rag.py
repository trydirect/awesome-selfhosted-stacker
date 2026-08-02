"""TDD tests for rag.py — mocked Ollama calls."""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch, MagicMock

from app.rag import generate_response, check_ollama_health, build_context


class _FakeResponse:
    """Mimics httpx.Response — json() returns dict, not coroutine."""
    def __init__(self, data):
        self._data = data
    def json(self):
        return self._data
    def raise_for_status(self):
        pass


class TestGenerateResponse:
    """BDD: RAG response generation"""

    @pytest.mark.asyncio
    @patch("app.rag.search_similar")
    @patch("app.rag.httpx.AsyncClient")
    async def test_generate_response_returns_reply(self, mock_httpx, mock_search):
        mock_search.return_value = [
            {"id": 1, "title": "Pricing", "source": "pricing", "content": "$29/mo", "score": 0.9}
        ]
        mock_client = MagicMock()
        mock_client.post = AsyncMock(return_value=_FakeResponse({"message": {"content": "Our plan costs $29/month."}}))
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_httpx.return_value = mock_client

        result = await generate_response("What does it cost?")
        assert "reply" in result
        assert result["reply"] == "Our plan costs $29/month."
        assert "sources" in result
        assert "confidence" in result

    @pytest.mark.asyncio
    @patch("app.rag.search_similar")
    @patch("app.rag.httpx.AsyncClient")
    async def test_generate_response_includes_sources(self, mock_httpx, mock_search):
        mock_search.return_value = [
            {"id": 1, "title": "FAQ", "source": "faq", "content": "Answer", "score": 0.85}
        ]
        mock_client = MagicMock()
        mock_client.post = AsyncMock(return_value=_FakeResponse({"message": {"content": "Here is the answer."}}))
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_httpx.return_value = mock_client

        result = await generate_response("question")
        assert len(result["sources"]) == 1
        assert result["sources"][0]["title"] == "FAQ"

    @pytest.mark.asyncio
    @patch("app.rag.search_similar")
    @patch("app.rag.httpx.AsyncClient")
    async def test_generate_response_with_history(self, mock_httpx, mock_search):
        mock_search.return_value = []
        mock_client = MagicMock()
        mock_client.post = AsyncMock(return_value=_FakeResponse({"message": {"content": "I don't know."}}))
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_httpx.return_value = mock_client

        history = [
            {"role": "user", "content": "Hi"},
            {"role": "assistant", "content": "Hello!"},
        ]
        result = await generate_response("How are you?", history=history)
        assert "reply" in result


class TestCheckOllamaHealth:
    """BDD: Ollama connectivity check"""

    @pytest.mark.asyncio
    @patch("app.rag.httpx.AsyncClient")
    async def test_health_check_returns_true_when_reachable(self, mock_httpx):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_client = MagicMock()
        mock_client.get = AsyncMock(return_value=mock_resp)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_httpx.return_value = mock_client

        assert await check_ollama_health() is True

    @pytest.mark.asyncio
    @patch("app.rag.httpx.AsyncClient")
    async def test_health_check_returns_false_when_unreachable(self, mock_httpx):
        mock_client = MagicMock()
        mock_client.get = AsyncMock(side_effect=Exception("Connection refused"))
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_httpx.return_value = mock_client

        assert await check_ollama_health() is False
