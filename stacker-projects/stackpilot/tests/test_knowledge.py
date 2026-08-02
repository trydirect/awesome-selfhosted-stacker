"""TDD tests for knowledge.py async functions — mocked DB and Ollama."""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch, MagicMock
import json
import inspect


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


from app.knowledge import add_document, search_similar, chunk_text


class TestAddDocument:
    """BDD: Document ingestion to knowledge base"""

    @pytest.mark.asyncio
    @patch("app.knowledge.get_db")
    @patch("app.knowledge.embed_batch")
    async def test_add_document_returns_doc_id(self, mock_embed, mock_db):
        mock_embed.return_value = [[0.1] * 768]
        mock_conn = AsyncMock()
        mock_conn.fetchrow.return_value = {"id": 1}
        mock_conn.execute.return_value = "INSERT 0 1"
        mock_db.return_value = _make_mock_pool(mock_conn)

        doc_id = await add_document("Test", "This is test content with enough length to chunk")
        assert doc_id == 1

    @pytest.mark.asyncio
    @patch("app.knowledge.get_db")
    @patch("app.knowledge.embed_batch")
    async def test_add_document_empty_content_returns_negative(self, mock_embed, mock_db):
        doc_id = await add_document("Test", "")
        assert doc_id == -1

    @pytest.mark.asyncio
    @patch("app.knowledge.get_db")
    @patch("app.knowledge.embed_batch")
    async def test_add_document_inserts_with_jsonb_metadata(self, mock_embed, mock_db):
        mock_embed.return_value = [[0.1] * 768]
        mock_conn = AsyncMock()
        mock_conn.fetchrow.return_value = {"id": 1}
        mock_conn.execute.return_value = "INSERT 0 1"
        mock_db.return_value = _make_mock_pool(mock_conn)

        await add_document("Test", "Content", metadata={"key": "value"})

        # Find the INSERT call (has ::jsonb cast)
        insert_call = None
        for call in mock_conn.fetchrow.call_args_list:
            if "jsonb" in str(call):
                insert_call = call
                break
        assert insert_call is not None
        meta_arg = insert_call[0][5]
        assert isinstance(meta_arg, str)
        parsed = json.loads(meta_arg)
        assert parsed == {"key": "value"}


class TestSearchSimilar:
    """BDD: Semantic search over knowledge base"""

    @pytest.mark.asyncio
    @patch("app.knowledge.get_redis")
    @patch("app.knowledge.get_db")
    @patch("app.knowledge.embed_text")
    async def test_search_returns_results(self, mock_embed, mock_db, mock_redis):
        mock_embed.return_value = [0.1] * 768
        mock_cache = AsyncMock()
        mock_cache.get.return_value = None
        mock_cache.setex.return_value = True
        mock_redis.return_value = mock_cache

        mock_conn = AsyncMock()
        mock_conn.fetch.return_value = [
            {"id": 1, "title": "Test", "source": "test", "content": "Hello", "metadata": {}, "score": 0.95}
        ]
        mock_db.return_value = _make_mock_pool(mock_conn)

        results = await search_similar("test query", limit=5)
        assert len(results) == 1
        assert results[0]["title"] == "Test"

    @pytest.mark.asyncio
    @patch("app.knowledge.get_redis")
    @patch("app.knowledge.get_db")
    @patch("app.knowledge.embed_text")
    async def test_search_returns_cached_results(self, mock_embed, mock_db, mock_redis):
        cached_data = [{"id": 1, "title": "Cached", "score": 0.9}]
        mock_cache = AsyncMock()
        mock_cache.get.return_value = json.dumps(cached_data)
        mock_redis.return_value = mock_cache

        results = await search_similar("cached query")
        assert len(results) == 1
        assert results[0]["title"] == "Cached"
        # DB should NOT be queried when cache hits
        mock_db.return_value.acquire.assert_not_called()
