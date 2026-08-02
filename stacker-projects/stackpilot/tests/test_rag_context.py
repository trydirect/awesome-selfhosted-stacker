"""TDD tests for RAG context building — pure function, no external dependencies."""

import pytest
from app.rag import build_context, SYSTEM_PROMPT


class TestBuildContext:
    """BDD: RAG Context Building feature"""

    def test_empty_results_produce_fallback(self):
        result = build_context([])
        assert result == "No relevant knowledge base entries found."

    def test_single_result_formatted(self):
        results = [
            {"title": "Pricing", "source": "https://example.com/pricing", "content": "Plans start at $29", "score": 0.95}
        ]
        ctx = build_context(results)
        assert "[Source 1: Pricing]" in ctx
        assert "relevance: 0.95" in ctx
        assert "Plans start at $29" in ctx

    def test_multiple_results_separated(self):
        results = [
            {"title": "A", "source": "a", "content": "content A", "score": 0.9},
            {"title": "B", "source": "b", "content": "content B", "score": 0.8},
            {"title": "C", "source": "c", "content": "content C", "score": 0.7},
        ]
        ctx = build_context(results)
        assert "[Source 1:" in ctx
        assert "[Source 2:" in ctx
        assert "[Source 3:" in ctx
        assert "---" in ctx

    def test_missing_title_uses_source(self):
        results = [
            {"title": "", "source": "https://example.com/about", "content": "About us", "score": 0.9}
        ]
        ctx = build_context(results)
        assert "https://example.com/about" in ctx

    def test_system_prompt_contains_context_placeholder(self):
        assert "{context}" in SYSTEM_PROMPT

    def test_context_is_injected_into_prompt(self):
        results = [
            {"title": "FAQ", "source": "faq", "content": "Answer", "score": 0.9}
        ]
        ctx = build_context(results)
        prompt = SYSTEM_PROMPT.format(context=ctx)
        assert "Answer" in prompt
        assert "FAQ" in prompt
