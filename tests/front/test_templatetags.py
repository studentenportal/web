import pytest

from apps.front.templatetags import tags
from apps.front.templatetags.md import render_markdown


@pytest.mark.parametrize(
    "arg, expected",
    [
        (0, []),
        (-5, []),
        (5, [0, 1, 2, 3, 4]),
    ],
)
def test_get_range(arg, expected):
    r = tags.get_range(arg)
    assert list(r) == expected


@pytest.mark.parametrize(
    "arg, expected",
    [
        (0, []),
        (1, [1]),
        (-5, []),
        (5, [1, 2, 3, 4, 5]),
    ],
)
def test_get_range1(arg, expected):
    r = tags.get_range1(arg)
    assert list(r) == expected


class TestRenderMarkdown:
    def test_basic_markdown(self):
        result = render_markdown("**bold** and *italic*")
        assert "<strong>bold</strong>" in result
        assert "<em>italic</em>" in result

    def test_newline_to_br(self):
        result = render_markdown("line1\nline2")
        assert "<br" in result

    def test_table(self):
        md = "| A | B |\n|---|---|\n| 1 | 2 |"
        result = render_markdown(md)
        assert "<table>" in result

    def test_xss_script_tag_stripped(self):
        result = render_markdown("<script>alert('xss')</script>")
        assert "<script>" not in result
        assert "alert" not in result

    def test_xss_onclick_stripped(self):
        result = render_markdown('<a onclick="alert(1)" href="ok">click</a>')
        assert "onclick" not in result
        assert 'href="ok"' in result

    def test_allowed_tags_preserved(self):
        result = render_markdown("# Heading\n\n- item1\n- item2")
        assert "<h1>" in result
        assert "<li>" in result

    def test_code_block(self):
        result = render_markdown("```\ncode here\n```")
        assert "<code>" in result
