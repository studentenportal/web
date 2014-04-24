import re
from django.template import Library

register = Library()


@register.filter
def get_range(value):
    """
    Filter - returns a list containing range made from given value
    Usage (in template):

    <ul>{% for i in 3|get_range %}
      <li>{{ i }}. Do something</li>
    {% endfor %}</ul>

    Results in the HTML:
    <ul>
      <li>0. Do something</li>
      <li>1. Do something</li>
      <li>2. Do something</li>
    </ul>

    Instead of 3 one may use the variable set in the views
    """
    return xrange(value)


@register.filter
def get_range1(value):
    """Like get_range, but with an 1 based index."""
    return xrange(1, value + 1)


@register.filter
def index(value, arg):
    """Return specified index of subscriptable element."""
    return value[int(arg)]


@register.filter
def lookup(dictionary, index):
    """Return index from dict."""
    if index in dictionary:
        return dictionary[index]
    return ''


@register.filter
def filetype_class(ext):
    """Returns the css class for a given file extension"""
    ext = ext.replace(".", "")

    if re.match("docx|xlsx|pptx", ext):
        ext = ext.replace("x", "")

    if re.match("pdf|doc|xls|ppt|zip", ext):
        return ext

    if re.match("gif|png|tiff|jpg|svg", ext):
        return "img"

    return "other"


@register.filter
def is_author(doc, user):
    """Returns whether the current user is the uploader of the given doc"""
    return doc.uploader == user


@register.filter()
def field_type(field):
    type_name = field.field.__class__.__name__
    types = {
        "FileField": "file",
        "TypedChoiceField": "checkbox",
        "CharField": "text"
    }
    return types[type_name] if type_name in types else type_name
