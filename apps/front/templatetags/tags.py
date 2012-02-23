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
def lookup(dict, index):
    """Return index from dict."""
    if index in dict:
        return dict[index]
    return ''
