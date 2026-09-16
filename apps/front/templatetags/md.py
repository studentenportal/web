import re

import bleach
import markdown
from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe

register = template.Library()

ALLOWED_TAGS = [
    "p", "br", "em", "strong", "ul", "ol", "li", "a",
    "code", "pre", "blockquote", "h1", "h2", "h3", "h4", "h5", "h6",
    "table", "thead", "tbody", "tr", "th", "td", "hr", "img",
]
ALLOWED_ATTRIBUTES = {
    "a": ["href"],
    "img": ["src", "alt"],
}


@register.filter
@stringfilter
def render_markdown(value):
    md = markdown.Markdown(extensions=["markdown.extensions.tables", "nl2br", "fenced_code"])
    html = md.convert(value)
    # Remove script and style tags with their content
    html = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r"<style[^>]*>.*?</style>", "", html, flags=re.DOTALL | re.IGNORECASE)
    clean = bleach.clean(html, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES, strip=True)
    return mark_safe(clean)
