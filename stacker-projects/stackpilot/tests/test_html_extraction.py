"""TDD tests for HTML extraction — pure functions, no external dependencies."""

import pytest
from app.knowledge import _extract_text, _extract_title, _extract_links


class TestExtractText:
    """BDD: HTML Text Extraction feature"""

    def test_extract_text_from_simple_html(self):
        html = "<html><body><p>Hello world</p></body></html>"
        text = _extract_text(html)
        assert "Hello world" in text

    def test_strip_script_tags(self):
        html = "<html><body><p>Hello</p><script>alert('hi')</script><p>World</p></body></html>"
        text = _extract_text(html)
        assert "Hello" in text
        assert "World" in text
        assert "alert" not in text

    def test_strip_style_tags(self):
        html = "<html><head><style>.red{color:red}</style></head><body><p>Content</p></body></html>"
        text = _extract_text(html)
        assert "Content" in text
        assert "color" not in text

    def test_strip_inline_scripts(self):
        html = "<div><p>Before</p><script type='text/javascript'>var x=1;</script><p>After</p></div>"
        text = _extract_text(html)
        assert "Before" in text
        assert "After" in text
        assert "var x" not in text

    def test_whitespace_normalization(self):
        html = "<p>  Hello   \n\n  world  </p>"
        text = _extract_text(html)
        assert "Hello world" in text

    def test_nested_tags(self):
        html = "<div><span><b>Bold</b> and <i>italic</i></span></div>"
        text = _extract_text(html)
        assert "Bold" in text
        assert "italic" in text

    def test_empty_html(self):
        assert _extract_text("") == ""

    def test_no_body_content(self):
        html = "<html><head></head></html>"
        text = _extract_text(html)
        assert text == ""


class TestExtractTitle:
    """BDD: HTML Title Extraction"""

    def test_extract_title(self):
        html = "<html><head><title>My Page</title></head><body></body></html>"
        assert _extract_title(html) == "My Page"

    def test_missing_title_returns_empty(self):
        html = "<html><body>No title here</body></html>"
        assert _extract_title(html) == ""

    def test_title_with_whitespace(self):
        html = "<html><head><title>  Spaced Title  </title></head></html>"
        assert _extract_title(html) == "Spaced Title"

    def test_case_insensitive_title(self):
        html = "<html><head><TITLE>Upper Title</TITLE></head></html>"
        assert _extract_title(html) == "Upper Title"


class TestExtractLinks:
    """BDD: HTML Link Extraction"""

    def test_extract_relative_links(self):
        html = '<a href="/about">About</a>'
        links = _extract_links(html, "https://example.com")
        assert len(links) == 1
        assert "about" in links[0]

    def test_extract_absolute_links(self):
        html = '<a href="https://example.com/contact">Contact</a>'
        links = _extract_links(html, "https://example.com")
        assert len(links) == 1
        assert "contact" in links[0]

    def test_skip_mailto_links(self):
        html = '<a href="mailto:test@example.com">Email</a>'
        links = _extract_links(html, "https://example.com")
        assert len(links) == 0

    def test_skip_javascript_links(self):
        html = '<a href="javascript:void(0)">Click</a>'
        links = _extract_links(html, "https://example.com")
        assert len(links) == 0

    def test_multiple_links(self):
        html = """
        <a href="/about">About</a>
        <a href="https://example.com/contact">Contact</a>
        <a href="/pricing">Pricing</a>
        """
        links = _extract_links(html, "https://example.com")
        assert len(links) == 3

    def test_relative_becomes_absolute(self):
        html = '<a href="/page">Page</a>'
        links = _extract_links(html, "https://example.com")
        assert links[0].startswith("https://example.com")
