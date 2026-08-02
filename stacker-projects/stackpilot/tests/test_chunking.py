"""TDD tests for text chunking — pure function, no external dependencies."""

import pytest
from app.knowledge import chunk_text


class TestChunkText:
    """BDD: Text Chunking feature"""

    def test_empty_text_produces_no_chunks(self):
        assert chunk_text("") == []

    def test_whitespace_only_produces_no_chunks(self):
        assert chunk_text("   ") == []

    def test_short_text_stays_in_one_chunk(self):
        result = chunk_text("Hello world")
        assert len(result) == 1
        assert result[0] == "Hello world"

    def test_long_text_splits_into_multiple_chunks(self):
        text = "word " * 200  # ~1000 chars
        result = chunk_text(text, chunk_size=500, overlap=100)
        assert len(result) >= 2

    def test_chunks_overlap(self):
        # Create text with distinct sections
        text = "A" * 400 + "SEPARATOR" + "B" * 400
        result = chunk_text(text, chunk_size=500, overlap=100)
        if len(result) >= 2:
            # End of chunk 0 should overlap with start of chunk 1
            end_of_0 = result[0][-100:]
            start_of_1 = result[1][:100]
            assert end_of_0 in result[1] or start_of_1 in result[0]

    def test_whitespace_is_normalized(self):
        result = chunk_text("  Hello   world  ")
        assert len(result) == 1
        assert result[0] == "Hello world"

    def test_exact_chunk_size_returns_one_chunk(self):
        text = "x" * 500
        result = chunk_text(text, chunk_size=500, overlap=100)
        assert len(result) == 1

    def test_text_just_over_chunk_size_splits(self):
        text = "x" * 501
        result = chunk_text(text, chunk_size=500, overlap=100)
        assert len(result) >= 2

    def test_no_empty_chunks(self):
        text = "a b c d e f g h i j " * 50
        result = chunk_text(text, chunk_size=50, overlap=10)
        for chunk in result:
            assert len(chunk.strip()) > 0
