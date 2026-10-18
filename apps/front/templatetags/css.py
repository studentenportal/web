import re
from pathlib import Path

from compressor.filters import FilterBase

IMPORT_RE = re.compile(
    r"@import\s+"
    r"(?:url\(\s*[\"']?(?P<url>[^\"')]+)[\"']?\s*\)"
    r"|[\"'](?P<str>[^\"']+)[\"'])"
    r"\s*;",
    re.IGNORECASE,
)

CHARSET_RE = re.compile(r"@charset\s+[\"'][^\"']+[\"']\s*;")


def _resolve_imports(css, base_dir, seen):
    def replace(match):
        path = match.group("url") or match.group("str")
        imported = (base_dir / path).resolve()
        if imported in seen:
            return ""
        seen.add(imported)
        try:
            content = imported.read_text(encoding="utf-8")
        except OSError:
            return match.group(0)
        content = CHARSET_RE.sub("", content, count=1)
        return _resolve_imports(content, imported.parent, seen)

    return IMPORT_RE.sub(replace, css)


def merge_minify_css(value, filename=None):
    if not filename:
        return value
    base_dir = Path(filename).resolve().parent
    seen = {Path(filename).resolve()}
    return _resolve_imports(value, base_dir, seen)


class MergeCSSFilter(FilterBase):
    def input(self, **kwargs):
        filename = kwargs.get("filename") or self.filename
        return merge_minify_css(self.content, filename)
