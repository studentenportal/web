# Tipps Enhancements Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Enhance the Tipps app with vote-based sorting, search, markdown rendering with WYSIWYG editor, an edit view, and a comment system.

**Architecture:** Build on the existing Tipps app (`apps/tipps/`) which uses Django class-based views, the shared `VotableModel`/`VoteViewMixin` voting system, and `extend_with_votes()` raw SQL annotations. New comment model follows Django conventions. Markdown rendered server-side with the existing `markdown` library, sanitized with `bleach`. EasyMDE loaded from CDN for the WYSIWYG editor.

**Tech Stack:** Django 5.0, PostgreSQL, markdown 3.10.2, bleach (new), EasyMDE (CDN), jQuery 2.1.0 (existing), pytest with django TestCase and model_bakery.

**Spec:** `docs/superpowers/specs/2026-09-12-tipps-enhancements-design.md`

## Global Constraints

- Python tests run via: `docker compose run --rm studentenportal_dev pytest tests/ -v` (from `/mnt/host-project/data/`)
- Django settings: `config.settings`, `DJANGO_SETTINGS_MODULE=config.settings`
- Test fixtures: `tests/conftest.py` provides `user` and `auth_client` fixtures (pytest)
- Baker recipe: `apps.front.user` creates user with username="testuser", password hash for "test"
- All German UI text (Swiss German locale: `de-ch`)
- Pagination template `front/blocks/pagination.html` uses `?page=N` — must be updated to preserve `sort` and `q` query params
- The `extend_with_votes()` function in `apps/front/voting.py` uses `.extra(select=...)` for SQL annotations — annotations include `upvote_count`, `downvote_count`, `vote_count`, `voted_up`, `voted_down`
- Existing test style mixes `TestCase` classes and pytest functions — new tests should use pytest functions with `@pytest.mark.django_db` for consistency with recent code
- EasyMDE CDN base: `https://cdn.jsdelivr.net/npm/easymde/dist/`

---

### Task 1: Move markdown filter to shared location and add XSS sanitization

**Files:**
- Create: `apps/front/templatetags/md.py`
- Modify: `apps/events/templatetags/md.py` (replace with import proxy)
- Modify: `requirements/base/requirements.txt` (add bleach)
- Test: `tests/front/test_templatetags.py` (add markdown tests)

**Interfaces:**
- Consumes: nothing
- Produces: `render_markdown` template filter in `apps.front.templatetags.md`, loaded via `{% load md %}` — converts markdown string to sanitized HTML string

- [ ] **Step 1: Add bleach to requirements**

In `requirements/base/requirements.txt`, add after the `markdown` line:

```
bleach==6.2.0
```

- [ ] **Step 2: Install bleach in the dev container**

Run:
```bash
docker compose run --rm studentenportal_dev pip install bleach==6.2.0
```

- [ ] **Step 3: Write failing tests for the markdown filter**

Add to `tests/front/test_templatetags.py`:

```python
import pytest

from apps.front.templatetags.md import render_markdown


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
```

- [ ] **Step 4: Run tests to verify they fail**

Run:
```bash
docker compose run --rm studentenportal_dev pytest tests/front/test_templatetags.py::TestRenderMarkdown -v
```
Expected: ImportError — `apps.front.templatetags.md` does not exist yet.

- [ ] **Step 5: Create the shared markdown filter**

Create `apps/front/templatetags/md.py`:

```python
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
    clean = bleach.clean(html, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES)
    return mark_safe(clean)
```

- [ ] **Step 6: Update events templatetag to proxy the shared filter**

Replace contents of `apps/events/templatetags/md.py` with:

```python
from apps.front.templatetags.md import register, render_markdown  # noqa: F401
```

This preserves `{% load md %}` in events templates without duplicating code.

- [ ] **Step 7: Run tests to verify they pass**

Run:
```bash
docker compose run --rm studentenportal_dev pytest tests/front/test_templatetags.py -v
```
Expected: All tests PASS.

- [ ] **Step 8: Commit**

```bash
git add apps/front/templatetags/md.py apps/events/templatetags/md.py requirements/base/requirements.txt tests/front/test_templatetags.py
git commit -m "feat: move markdown filter to shared location with XSS sanitization via bleach"
```

---

### Task 2: Vote-based sorting with toggle and search

**Files:**
- Modify: `apps/tipps/views.py` (TippList — add sorting and search)
- Modify: `apps/tipps/templates/tipps/tipp_list.html` (add sort toggle, search bar)
- Modify: `apps/front/templates/front/blocks/pagination.html` (preserve query params)
- Test: `tests/tipps/__init__.py` (create)
- Test: `tests/tipps/test_views.py` (create)

**Interfaces:**
- Consumes: `extend_with_votes()` from `apps.front.voting` (existing)
- Produces: TippList view with `?sort=votes|date` and `?q=searchterm` query parameters; `get_context_data()` passes `current_sort` and `search_query` to template

- [ ] **Step 1: Create test directory**

Create `tests/tipps/__init__.py` (empty file).

- [ ] **Step 2: Write failing tests for sorting and search**

Create `tests/tipps/test_views.py`:

```python
import pytest
from django.contrib.auth import get_user_model

from apps.tipps.models import Tipp, TippVote

User = get_user_model()


@pytest.fixture
def user2(db):
    return User.objects.create_user(
        username="testuser2", password="test", email="test2@studentenportal.ch"
    )


@pytest.fixture
def tipps_with_votes(user, user2):
    """Create 3 tipps with different vote counts:
    tipp_popular: 2 upvotes (by user and user2)
    tipp_medium: 1 upvote (by user)
    tipp_new: 0 votes but newest
    """
    tipp_popular = Tipp.objects.create(
        author=user, summary="Popular Tipp", description="Very popular"
    )
    TippVote.objects.create(user=user, tipp=tipp_popular, vote=True)
    TippVote.objects.create(user=user2, tipp=tipp_popular, vote=True)

    tipp_medium = Tipp.objects.create(
        author=user, summary="Medium Tipp", description="Medium popular"
    )
    TippVote.objects.create(user=user, tipp=tipp_medium, vote=True)

    tipp_new = Tipp.objects.create(
        author=user, summary="New Tipp", description="Brand new"
    )

    return tipp_popular, tipp_medium, tipp_new


@pytest.mark.django_db
class TestTippListSorting:
    def test_default_sort_by_votes(self, auth_client, tipps_with_votes):
        tipp_popular, tipp_medium, tipp_new = tipps_with_votes
        response = auth_client.get("/tipps/")
        content = response.content.decode()
        pos_popular = content.index("Popular Tipp")
        pos_medium = content.index("Medium Tipp")
        pos_new = content.index("New Tipp")
        assert pos_popular < pos_medium, "Popular tipp should appear before medium"
        assert pos_medium < pos_new, "Medium tipp should appear before new"

    def test_sort_by_votes_explicit(self, auth_client, tipps_with_votes):
        tipp_popular, tipp_medium, tipp_new = tipps_with_votes
        response = auth_client.get("/tipps/?sort=votes")
        content = response.content.decode()
        pos_popular = content.index("Popular Tipp")
        pos_new = content.index("New Tipp")
        assert pos_popular < pos_new

    def test_sort_by_date(self, auth_client, tipps_with_votes):
        tipp_popular, tipp_medium, tipp_new = tipps_with_votes
        response = auth_client.get("/tipps/?sort=date")
        content = response.content.decode()
        pos_new = content.index("New Tipp")
        pos_popular = content.index("Popular Tipp")
        assert pos_new < pos_popular, "Newest tipp should appear first when sorting by date"

    def test_sort_toggle_links_present(self, auth_client, tipps_with_votes):
        response = auth_client.get("/tipps/")
        content = response.content.decode()
        assert "Beliebteste" in content
        assert "Neueste" in content


@pytest.mark.django_db
class TestTippListSearch:
    def test_search_by_summary(self, auth_client, user):
        Tipp.objects.create(author=user, summary="Python Tricks", description="desc")
        Tipp.objects.create(author=user, summary="Other Tipp", description="desc")
        response = auth_client.get("/tipps/?q=Python")
        content = response.content.decode()
        assert "Python Tricks" in content
        assert "Other Tipp" not in content

    def test_search_by_description(self, auth_client, user):
        Tipp.objects.create(author=user, summary="Tipp A", description="Use virtualenv")
        Tipp.objects.create(author=user, summary="Tipp B", description="Something else")
        response = auth_client.get("/tipps/?q=virtualenv")
        content = response.content.decode()
        assert "Tipp A" in content
        assert "Tipp B" not in content

    def test_search_no_results(self, auth_client, user):
        Tipp.objects.create(author=user, summary="Tipp A", description="desc")
        response = auth_client.get("/tipps/?q=nonexistent")
        content = response.content.decode()
        assert "Keine Tipps gefunden" in content

    def test_search_preserves_sort(self, auth_client, user):
        Tipp.objects.create(author=user, summary="Searchable", description="desc")
        response = auth_client.get("/tipps/?q=Searchable&sort=date")
        assert response.status_code == 200
        content = response.content.decode()
        assert "Searchable" in content

    def test_search_term_persists_in_input(self, auth_client, user):
        Tipp.objects.create(author=user, summary="Tipp", description="desc")
        response = auth_client.get("/tipps/?q=findme")
        content = response.content.decode()
        assert 'value="findme"' in content
```

- [ ] **Step 3: Run tests to verify they fail**

Run:
```bash
docker compose run --rm studentenportal_dev pytest tests/tipps/test_views.py -v
```
Expected: FAIL — no sorting, no search, no template changes.

- [ ] **Step 4: Implement sorting and search in TippList view**

Replace `apps/tipps/views.py` with:

```python
from django.contrib import messages
from django.db.models import Q
from django.urls import reverse
from django.views.generic.edit import CreateView, DeleteView
from django.views.generic.list import ListView

from apps.front.mixins import (
    AutoUpvoteCreateMixin,
    LoginRequiredMixin,
    OwnerDeleteMixin,
)
from apps.front.voting import VoteViewMixin, extend_with_votes
from apps.tipps import forms, models


class TippList(ListView):
    paginate_by = 50

    def get_queryset(self):
        qs = extend_with_votes(
            models.Tipp.objects.all(),
            "tipps_tippvote",
            "tipp_id",
            "tipps_tipp",
            self.request.user.pk,
        )

        # Search
        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(Q(summary__icontains=q) | Q(description__icontains=q))

        # Sort
        sort = self.request.GET.get("sort", "votes")
        if sort == "date":
            qs = qs.order_by("-date")
        else:
            qs = qs.order_by("-upvote_count", "-date")

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["current_sort"] = self.request.GET.get("sort", "votes")
        context["search_query"] = self.request.GET.get("q", "")
        return context


class TippAdd(LoginRequiredMixin, AutoUpvoteCreateMixin, CreateView):
    model = models.Tipp
    form_class = forms.TippForm
    vote_model = models.TippVote
    item_fk_name = "tipp"

    def get_success_url(self):
        messages.add_message(
            self.request,
            messages.SUCCESS,
            'Tipp "%s" wurde erfolgreich hinzugefügt.' % self.object.summary,
        )
        return reverse("tipps:tipp_list")


class TippDelete(LoginRequiredMixin, OwnerDeleteMixin, DeleteView):
    model = models.Tipp
    forbidden_message = "Du darfst keine fremden Tipps löschen."
    success_message = "Tipp wurde erfolgreich gelöscht."
    event_name = "tipp_delete"
    success_url_name = "tipps:tipp_list"


class TippVote(LoginRequiredMixin, VoteViewMixin):
    item_model = models.Tipp
    vote_model = models.TippVote
    item_fk_name = "tipp"
```

- [ ] **Step 5: Update tipp_list.html with sort toggle, search bar, and query-preserving links**

Replace `apps/tipps/templates/tipps/tipp_list.html` with:

```html
{% extends 'base.html' %} {% load tabs %}
{% load thumbnail %}
{% load compress %}

{% block title %}Tipps und Tricks{% endblock %}

{% block bodyclass %}tipp_list{% endblock %}

{% block navigation %}
    {% activetab 'navigation' 'tipps' %}
    {{ block.super }}
{% endblock %}

{% block scripts %}
    {{ block.super }}
    {% compress js %}
       <script src="{{ STATIC_URL }}js/votes.js"></script>
    {% endcompress %}
{% endblock %}

{% block content %}

    <div class="page-header">
        <h1>Tipps und Tricks</h1>
    </div>

    <form method="get" action="{% url 'tipps:tipp_list' %}" class="search-form">
        <input type="text" name="q" value="{{ search_query }}" placeholder="Tipps durchsuchen..." />
        {% if current_sort != "votes" %}
            <input type="hidden" name="sort" value="{{ current_sort }}" />
        {% endif %}
        <button type="submit" class="button">Suchen</button>
    </form>

    <div class="sort-toggle">
        <a class="button{% if current_sort == 'votes' %} button-primary{% endif %}" href="?sort=votes{% if search_query %}&q={{ search_query }}{% endif %}">Beliebteste</a>
        <a class="button{% if current_sort == 'date' %} button-primary{% endif %}" href="?sort=date{% if search_query %}&q={{ search_query }}{% endif %}">Neueste</a>
    </div>

    {% if user.is_authenticated %}
        <a class="button button-primary" href="{% url 'tipps:tipp_add' %}">
            Tipp hinzufügen
        </a>
    {% endif %}

    {% if object_list %}

    {% include 'front/blocks/pagination.html' %}

    {% for tipp in object_list %}
        <article class="quote {% if tipp.author_id == user.pk %}quote-edit{% endif %}">
          {% if tipp.author_id == user.pk %}
              <div class="edit">
                  {% url 'tipps:tipp_delete' tipp.pk as delete_url %}
                  {% include 'front/blocks/delete_button.html' with small_button=1 delete_url=delete_url %}
              </div>
          {% endif %}
          {% url 'tipps:tipp_vote' tipp.pk as vote_url %}
          {% include 'front/blocks/vote_buttons.html' with vote_elem=tipp vote_url=vote_url %}
          <div class="quote-wrapper">
            <p><em>{{ tipp.summary }}</em></p>
            {% if tipp.author %}
                <a rel="author" href="{% url 'user' tipp.author.pk tipp.author.username|slugify %}">{{ tipp.author.name }}</a>
            {% else %}
                <span class="author">Gelöschter User</span>
            {% endif %}
            <p>{{ tipp.description }}</p>
            <p>{{ tipp.date|date }}</p>
          </div>
        </article>
    {% endfor %}

    {% include 'front/blocks/pagination.html' %}

    {% else %}
        <p><em>Keine Tipps gefunden.</em></p>
    {% endif %}

{% endblock %}
```

- [ ] **Step 6: Update pagination template to preserve query params**

The shared pagination template (`apps/front/templates/front/blocks/pagination.html`) currently hardcodes `?page=N`, which loses `sort` and `q` parameters. Update it to build URLs that preserve existing query params.

Replace `apps/front/templates/front/blocks/pagination.html` with:

```html
{% load tags %}
{% if paginator.num_pages > 1 %}
<ul class="pagination">
    {% if page_obj.has_previous %}
        <li><a class="button" href="?{% for key, value in request.GET.items %}{% if key != 'page' %}{{ key }}={{ value }}&{% endif %}{% endfor %}page={{ page_obj.previous_page_number }}">&laquo;</a></li>
    {% endif %}

    {% for num in page_obj.paginator.page_range|pagination_slice:page_obj.number %}
        {% if num == page_obj.number %}
            <li><a class="button button-primary" href="#">{{ num }}</a></li>
        {% else %}
            <li><a class="button" href="?{% for key, value in request.GET.items %}{% if key != 'page' %}{{ key }}={{ value }}&{% endif %}{% endfor %}page={{ num }}">{{ num }}</a></li>
        {% endif %}
    {% endfor %}

    {% if page_obj.has_next %}
        <li><a class="button" href="?{% for key, value in request.GET.items %}{% if key != 'page' %}{{ key }}={{ value }}&{% endif %}{% endfor %}page={{ page_obj.next_page_number }}">&raquo;</a></li>
    {% endif %}
<ul>
{% endif %}
```

- [ ] **Step 7: Run tests to verify they pass**

Run:
```bash
docker compose run --rm studentenportal_dev pytest tests/tipps/test_views.py -v
```
Expected: All tests PASS.

- [ ] **Step 8: Run full test suite to check for regressions**

Run:
```bash
docker compose run --rm studentenportal_dev pytest tests/ -v
```
Expected: All existing tests still PASS.

- [ ] **Step 9: Commit**

```bash
git add tests/tipps/ apps/tipps/views.py apps/tipps/templates/tipps/tipp_list.html apps/front/templates/front/blocks/pagination.html
git commit -m "feat: add vote-based sorting with toggle and search to tipps list"
```

---

### Task 3: Markdown rendering in tipps and EasyMDE WYSIWYG editor

**Files:**
- Modify: `apps/tipps/templates/tipps/tipp_list.html` (apply render_markdown filter)
- Modify: `apps/tipps/templates/tipps/tipp_form.html` (add EasyMDE)
- Test: `tests/tipps/test_views.py` (add markdown rendering test)

**Interfaces:**
- Consumes: `render_markdown` filter from `apps.front.templatetags.md` (Task 1)
- Produces: Tipp descriptions rendered as HTML in list view; EasyMDE editor on add/edit forms

- [ ] **Step 1: Write failing test for markdown rendering in tipp list**

Add to `tests/tipps/test_views.py`:

```python
@pytest.mark.django_db
class TestTippMarkdownRendering:
    def test_markdown_rendered_in_list(self, auth_client, user):
        Tipp.objects.create(
            author=user, summary="MD Tipp", description="**bold text** and *italic*"
        )
        response = auth_client.get("/tipps/")
        content = response.content.decode()
        assert "<strong>bold text</strong>" in content
        assert "<em>italic</em>" in content

    def test_xss_stripped_in_list(self, auth_client, user):
        Tipp.objects.create(
            author=user,
            summary="XSS Tipp",
            description="<script>alert('xss')</script>",
        )
        response = auth_client.get("/tipps/")
        content = response.content.decode()
        assert "<script>" not in content
```

- [ ] **Step 2: Run test to verify it fails**

Run:
```bash
docker compose run --rm studentenportal_dev pytest tests/tipps/test_views.py::TestTippMarkdownRendering -v
```
Expected: FAIL — description rendered as plain text, no `<strong>` tags.

- [ ] **Step 3: Add markdown rendering to tipp_list.html**

In `apps/tipps/templates/tipps/tipp_list.html`, add `{% load md %}` after the existing load tags at the top:

```html
{% extends 'base.html' %} {% load tabs %}
{% load thumbnail %}
{% load compress %}
{% load md %}
```

And change the description line from:
```html
            <p>{{ tipp.description }}</p>
```
to:
```html
            <div class="tipp-description">{{ tipp.description|render_markdown }}</div>
```

(Use `<div>` instead of `<p>` because markdown output already contains `<p>` tags.)

- [ ] **Step 4: Add EasyMDE to tipp_form.html**

Replace `apps/tipps/templates/tipps/tipp_form.html` with:

```html
{% extends 'base.html' %}
{% load tabs %}

{% block title %}Tipp hinzufügen{% endblock %}

{% block navigation %}
    {% activetab 'navigation' 'tipps' %}
    {{ block.super }}
{% endblock %}

{% block extra_head %}
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/easymde/dist/easymde.min.css">
{% endblock %}

{% block content %}
    <div class="page-header">
        <h1>Tipp hinzufügen</h1>
    </div>

    <form method="POST" class="form-horizontal">{% csrf_token %}
        {% include 'lib/form_loop.html' %}
        <div class="form-actions">
            <button type="submit" class="button button-primary">Eintragen</button>
            <a href="{% url 'tipps:tipp_list' %}" class="button">Abbrechen</a>
        </div>
    </form>

    <script src="https://cdn.jsdelivr.net/npm/easymde/dist/easymde.min.js"></script>
    <script>
        var descField = document.getElementById('id_description');
        if (descField) {
            new EasyMDE({
                element: descField,
                spellChecker: false,
                status: false,
            });
        }
    </script>
{% endblock %}
```

Note: Check if `base.html` has an `extra_head` block. If not, the CSS link needs to go inside the `content` block above the form. Let the implementer check `base.html` for available blocks and adjust accordingly — the key requirement is: load `easymde.min.css` before the form, load `easymde.min.js` after it, then initialize.

- [ ] **Step 5: Run tests to verify they pass**

Run:
```bash
docker compose run --rm studentenportal_dev pytest tests/tipps/test_views.py -v
```
Expected: All tests PASS.

- [ ] **Step 6: Commit**

```bash
git add apps/tipps/templates/tipps/tipp_list.html apps/tipps/templates/tipps/tipp_form.html
git commit -m "feat: add markdown rendering to tipps list and EasyMDE editor to form"
```

---

### Task 4: Tipp edit view

**Files:**
- Modify: `apps/tipps/views.py` (add TippEdit view)
- Modify: `apps/tipps/urls.py` (add edit URL)
- Modify: `apps/tipps/templates/tipps/tipp_list.html` (add edit button)
- Test: `tests/tipps/test_views.py` (add edit tests)

**Interfaces:**
- Consumes: `TippForm` from `apps.tipps.forms`, `LoginRequiredMixin` from `apps.front.mixins`
- Produces: `TippEdit` view at `/tipps/<pk>/edit/`, URL name `tipps:tipp_edit`

- [ ] **Step 1: Write failing tests for the edit view**

Add to `tests/tipps/test_views.py`:

```python
@pytest.mark.django_db
class TestTippEdit:
    def test_author_can_edit(self, auth_client, user):
        tipp = Tipp.objects.create(
            author=user, summary="Original", description="Original desc"
        )
        response = auth_client.get(f"/tipps/{tipp.pk}/edit/")
        assert response.status_code == 200
        assert "Original" in response.content.decode()

    def test_author_can_submit_edit(self, auth_client, user):
        tipp = Tipp.objects.create(
            author=user, summary="Original", description="Original desc"
        )
        response = auth_client.post(
            f"/tipps/{tipp.pk}/edit/",
            {"summary": "Updated", "description": "Updated desc"},
        )
        assert response.status_code == 302
        tipp.refresh_from_db()
        assert tipp.summary == "Updated"
        assert tipp.description == "Updated desc"

    def test_non_author_gets_403(self, auth_client, user, user2):
        tipp = Tipp.objects.create(
            author=user2, summary="Other", description="Other desc"
        )
        response = auth_client.get(f"/tipps/{tipp.pk}/edit/")
        assert response.status_code == 403

    def test_anonymous_redirected_to_login(self, client, user):
        tipp = Tipp.objects.create(
            author=user, summary="Test", description="desc"
        )
        response = client.get(f"/tipps/{tipp.pk}/edit/")
        assert response.status_code == 302
        assert "/accounts/login/" in response.url

    def test_edit_button_visible_to_author(self, auth_client, user):
        Tipp.objects.create(author=user, summary="My Tipp", description="desc")
        response = auth_client.get("/tipps/")
        content = response.content.decode()
        assert "Bearbeiten" in content

    def test_edit_button_not_visible_to_others(self, auth_client, user2):
        Tipp.objects.create(author=user2, summary="Other Tipp", description="desc")
        response = auth_client.get("/tipps/")
        content = response.content.decode()
        assert "Bearbeiten" not in content
```

- [ ] **Step 2: Run tests to verify they fail**

Run:
```bash
docker compose run --rm studentenportal_dev pytest tests/tipps/test_views.py::TestTippEdit -v
```
Expected: FAIL — URL not found (404/NoReverseMatch).

- [ ] **Step 3: Add TippEdit view to views.py**

Add these imports to the top of `apps/tipps/views.py` (merge with existing):

```python
from django.http import HttpResponseForbidden
from django.views.generic.edit import CreateView, DeleteView, UpdateView
```

Add the view class after `TippAdd`:

```python
class TippEdit(LoginRequiredMixin, UpdateView):
    model = models.Tipp
    form_class = forms.TippForm
    template_name = "tipps/tipp_form.html"

    def dispatch(self, request, *args, **kwargs):
        tipp = self.get_object()
        if tipp.author != request.user:
            return HttpResponseForbidden("Du darfst keine fremden Tipps bearbeiten.")
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        messages.add_message(
            self.request,
            messages.SUCCESS,
            'Tipp "%s" wurde erfolgreich aktualisiert.' % self.object.summary,
        )
        return reverse("tipps:tipp_list")
```

- [ ] **Step 4: Add edit URL to urls.py**

Add to `apps/tipps/urls.py` urlpatterns list:

```python
    re_path(
        r"^(?P<pk>-?\d+)/edit/$",
        views.TippEdit.as_view(),
        name="tipp_edit",
    ),
```

- [ ] **Step 5: Add edit button to tipp_list.html**

In `apps/tipps/templates/tipps/tipp_list.html`, inside the `{% if tipp.author_id == user.pk %}` block, add an edit button next to the delete button:

```html
          {% if tipp.author_id == user.pk %}
              <div class="edit">
                  <a class="button" href="{% url 'tipps:tipp_edit' tipp.pk %}">Bearbeiten</a>
                  {% url 'tipps:tipp_delete' tipp.pk as delete_url %}
                  {% include 'front/blocks/delete_button.html' with small_button=1 delete_url=delete_url %}
              </div>
          {% endif %}
```

- [ ] **Step 6: Run tests to verify they pass**

Run:
```bash
docker compose run --rm studentenportal_dev pytest tests/tipps/test_views.py -v
```
Expected: All tests PASS.

- [ ] **Step 7: Run full test suite**

Run:
```bash
docker compose run --rm studentenportal_dev pytest tests/ -v
```
Expected: All tests PASS.

- [ ] **Step 8: Commit**

```bash
git add apps/tipps/views.py apps/tipps/urls.py apps/tipps/templates/tipps/tipp_list.html
git commit -m "feat: add tipp edit view with author-only access"
```

---

### Task 5: Comment model, migration, admin, and form

**Files:**
- Modify: `apps/tipps/models.py` (add TippComment)
- Modify: `apps/tipps/admin.py` (register TippComment)
- Modify: `apps/tipps/forms.py` (add TippCommentForm)
- Create: migration (auto-generated)
- Test: `tests/tipps/test_models.py` (create)

**Interfaces:**
- Consumes: `Tipp` model from `apps.tipps.models`
- Produces: `TippComment` model with fields `tipp` (FK), `author` (FK), `text` (TextField), `date` (auto). `TippCommentForm` with single field `text`. Admin registered with `list_display`.

- [ ] **Step 1: Write failing tests for the comment model**

Create `tests/tipps/test_models.py`:

```python
import pytest
from django.contrib.auth import get_user_model

from apps.tipps.models import Tipp, TippComment

User = get_user_model()


@pytest.mark.django_db
class TestTippComment:
    def test_create_comment(self, user):
        tipp = Tipp.objects.create(author=user, summary="Test", description="desc")
        comment = TippComment.objects.create(tipp=tipp, author=user, text="Nice tipp!")
        assert comment.pk is not None
        assert comment.text == "Nice tipp!"
        assert comment.tipp == tipp
        assert comment.author == user

    def test_comment_ordering_oldest_first(self, user):
        tipp = Tipp.objects.create(author=user, summary="Test", description="desc")
        c1 = TippComment.objects.create(tipp=tipp, author=user, text="First")
        c2 = TippComment.objects.create(tipp=tipp, author=user, text="Second")
        comments = list(tipp.comments.all())
        assert comments == [c1, c2]

    def test_comment_cascade_delete(self, user):
        tipp = Tipp.objects.create(author=user, summary="Test", description="desc")
        TippComment.objects.create(tipp=tipp, author=user, text="Comment")
        assert TippComment.objects.count() == 1
        tipp.delete()
        assert TippComment.objects.count() == 0

    def test_comment_author_set_null(self, user):
        tipp = Tipp.objects.create(author=user, summary="Test", description="desc")
        comment = TippComment.objects.create(tipp=tipp, author=user, text="Comment")
        user.delete()
        comment.refresh_from_db()
        assert comment.author is None

    def test_str(self, user):
        tipp = Tipp.objects.create(author=user, summary="Test", description="desc")
        comment = TippComment.objects.create(tipp=tipp, author=user, text="Comment")
        assert "testuser" in str(comment)
        assert str(tipp.pk) in str(comment)
```

- [ ] **Step 2: Run tests to verify they fail**

Run:
```bash
docker compose run --rm studentenportal_dev pytest tests/tipps/test_models.py -v
```
Expected: FAIL — `TippComment` does not exist.

- [ ] **Step 3: Add TippComment model**

Add to `apps/tipps/models.py` after the `TippVote` class:

```python
class TippComment(models.Model):
    """A comment on a tipp."""

    tipp = models.ForeignKey(Tipp, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="tipp_comments",
    )
    text = models.TextField("Kommentar")
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["date"]

    def __str__(self):
        return f"Comment by {self.author} on Tipp {self.tipp_id}"
```

- [ ] **Step 4: Create and run migration**

Run:
```bash
docker compose run --rm studentenportal_dev python manage.py makemigrations tipps
docker compose run --rm studentenportal_dev python manage.py migrate
```

- [ ] **Step 5: Add TippCommentForm to forms.py**

Add to `apps/tipps/forms.py`:

```python
class TippCommentForm(forms.ModelForm):
    class Meta:
        model = models.TippComment
        fields = ("text",)
```

- [ ] **Step 6: Update admin.py**

Replace `apps/tipps/admin.py` with:

```python
from django.contrib import admin

from apps.tipps import models


@admin.register(models.Tipp)
class TippAdmin(admin.ModelAdmin):
    pass


@admin.register(models.TippComment)
class TippCommentAdmin(admin.ModelAdmin):
    list_display = ("tipp", "author", "date")
    list_filter = ("date",)
```

- [ ] **Step 7: Run tests to verify they pass**

Run:
```bash
docker compose run --rm studentenportal_dev pytest tests/tipps/test_models.py -v
```
Expected: All tests PASS.

- [ ] **Step 8: Commit**

```bash
git add apps/tipps/models.py apps/tipps/forms.py apps/tipps/admin.py apps/tipps/migrations/ tests/tipps/test_models.py
git commit -m "feat: add TippComment model, form, admin, and migration"
```

---

### Task 6: Comment views (add, edit, delete) and templates

**Files:**
- Modify: `apps/tipps/views.py` (add comment views)
- Modify: `apps/tipps/urls.py` (add comment URLs)
- Modify: `apps/tipps/templates/tipps/tipp_list.html` (add comment section)
- Create: `apps/tipps/templates/tipps/comment_form.html`
- Create: `apps/tipps/templates/tipps/comment_confirm_delete.html`
- Test: `tests/tipps/test_views.py` (add comment view tests)

**Interfaces:**
- Consumes: `TippComment` model, `TippCommentForm` from Task 5. `LoginRequiredMixin` from `apps.front.mixins`.
- Produces: `TippCommentAdd` (POST, creates comment), `TippCommentEdit` (GET/POST, author only), `TippCommentDelete` (GET/POST, author or staff). Comment section in tipp list with toggle, count badge, inline add form.

- [ ] **Step 1: Write failing tests for comment views**

Add to `tests/tipps/test_views.py`:

```python
from apps.tipps.models import Tipp, TippVote, TippComment


@pytest.fixture
def staff_user(db):
    return User.objects.create_user(
        username="admin", password="test", email="admin@studentenportal.ch",
        is_staff=True,
    )


@pytest.fixture
def staff_client(client, staff_user):
    assert client.login(username="admin", password="test")
    return client


@pytest.mark.django_db
class TestTippCommentAdd:
    def test_authenticated_user_can_add_comment(self, auth_client, user):
        tipp = Tipp.objects.create(author=user, summary="Test", description="desc")
        response = auth_client.post(
            f"/tipps/{tipp.pk}/comment/add/",
            {"text": "Great tipp!"},
        )
        assert response.status_code == 302
        assert TippComment.objects.filter(tipp=tipp, text="Great tipp!").exists()

    def test_anonymous_cannot_add_comment(self, client, user):
        tipp = Tipp.objects.create(author=user, summary="Test", description="desc")
        response = client.post(
            f"/tipps/{tipp.pk}/comment/add/",
            {"text": "Nope"},
        )
        assert response.status_code == 302
        assert "/accounts/login/" in response.url
        assert TippComment.objects.count() == 0

    def test_comment_sets_author(self, auth_client, user):
        tipp = Tipp.objects.create(author=user, summary="Test", description="desc")
        auth_client.post(f"/tipps/{tipp.pk}/comment/add/", {"text": "Comment"})
        comment = TippComment.objects.first()
        assert comment.author == user


@pytest.mark.django_db
class TestTippCommentEdit:
    def test_author_can_edit_comment(self, auth_client, user):
        tipp = Tipp.objects.create(author=user, summary="Test", description="desc")
        comment = TippComment.objects.create(tipp=tipp, author=user, text="Original")
        response = auth_client.post(
            f"/tipps/comment/{comment.pk}/edit/",
            {"text": "Updated"},
        )
        assert response.status_code == 302
        comment.refresh_from_db()
        assert comment.text == "Updated"

    def test_non_author_gets_403(self, auth_client, user, user2):
        tipp = Tipp.objects.create(author=user2, summary="Test", description="desc")
        comment = TippComment.objects.create(tipp=tipp, author=user2, text="Other")
        response = auth_client.get(f"/tipps/comment/{comment.pk}/edit/")
        assert response.status_code == 403

    def test_anonymous_redirected_to_login(self, client, user):
        tipp = Tipp.objects.create(author=user, summary="Test", description="desc")
        comment = TippComment.objects.create(tipp=tipp, author=user, text="Test")
        response = client.get(f"/tipps/comment/{comment.pk}/edit/")
        assert response.status_code == 302
        assert "/accounts/login/" in response.url


@pytest.mark.django_db
class TestTippCommentDelete:
    def test_author_can_delete_comment(self, auth_client, user):
        tipp = Tipp.objects.create(author=user, summary="Test", description="desc")
        comment = TippComment.objects.create(tipp=tipp, author=user, text="Delete me")
        response = auth_client.post(f"/tipps/comment/{comment.pk}/delete/")
        assert response.status_code == 302
        assert TippComment.objects.count() == 0

    def test_admin_can_delete_any_comment(self, staff_client, user):
        tipp = Tipp.objects.create(author=user, summary="Test", description="desc")
        comment = TippComment.objects.create(tipp=tipp, author=user, text="Delete me")
        response = staff_client.post(f"/tipps/comment/{comment.pk}/delete/")
        assert response.status_code == 302
        assert TippComment.objects.count() == 0

    def test_non_author_non_admin_gets_403(self, auth_client, user, user2):
        tipp = Tipp.objects.create(author=user2, summary="Test", description="desc")
        comment = TippComment.objects.create(tipp=tipp, author=user2, text="Protected")
        response = auth_client.post(f"/tipps/comment/{comment.pk}/delete/")
        assert response.status_code == 403
        assert TippComment.objects.count() == 1


@pytest.mark.django_db
class TestTippCommentInList:
    def test_comment_count_displayed(self, auth_client, user):
        tipp = Tipp.objects.create(author=user, summary="Test", description="desc")
        TippComment.objects.create(tipp=tipp, author=user, text="Comment 1")
        TippComment.objects.create(tipp=tipp, author=user, text="Comment 2")
        response = auth_client.get("/tipps/")
        content = response.content.decode()
        assert "2 Kommentare" in content

    def test_zero_comments_displayed(self, auth_client, user):
        Tipp.objects.create(author=user, summary="Test", description="desc")
        response = auth_client.get("/tipps/")
        content = response.content.decode()
        assert "0 Kommentare" in content

    def test_comment_add_form_present_for_authenticated(self, auth_client, user):
        Tipp.objects.create(author=user, summary="Test", description="desc")
        response = auth_client.get("/tipps/")
        content = response.content.decode()
        assert "Kommentar hinzufügen" in content or 'name="text"' in content
```

- [ ] **Step 2: Run tests to verify they fail**

Run:
```bash
docker compose run --rm studentenportal_dev pytest tests/tipps/test_views.py::TestTippCommentAdd -v
```
Expected: FAIL — URL not found.

- [ ] **Step 3: Add comment views to views.py**

Add these imports at the top of `apps/tipps/views.py` (merge with existing):

```python
from django.db.models import Count, Q
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect
from django.views.generic.edit import CreateView, DeleteView, UpdateView
```

Add comment views at the end of `apps/tipps/views.py`:

```python
class TippCommentAdd(LoginRequiredMixin, CreateView):
    model = models.TippComment
    form_class = forms.TippCommentForm

    def get(self, request, *args, **kwargs):
        return redirect(reverse("tipps:tipp_list"))

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.tipp = get_object_or_404(models.Tipp, pk=self.kwargs["pk"])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("tipps:tipp_list")


class TippCommentEdit(LoginRequiredMixin, UpdateView):
    model = models.TippComment
    form_class = forms.TippCommentForm
    template_name = "tipps/comment_form.html"

    def dispatch(self, request, *args, **kwargs):
        comment = self.get_object()
        if comment.author != request.user:
            return HttpResponseForbidden("Du darfst keine fremden Kommentare bearbeiten.")
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        messages.add_message(
            self.request, messages.SUCCESS, "Kommentar wurde aktualisiert."
        )
        return reverse("tipps:tipp_list")


class TippCommentDelete(LoginRequiredMixin, DeleteView):
    model = models.TippComment
    template_name = "tipps/comment_confirm_delete.html"

    def dispatch(self, request, *args, **kwargs):
        comment = self.get_object()
        if comment.author != request.user and not request.user.is_staff:
            return HttpResponseForbidden("Du darfst keine fremden Kommentare löschen.")
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        messages.add_message(
            self.request, messages.SUCCESS, "Kommentar wurde gelöscht."
        )
        return reverse("tipps:tipp_list")
```

Also update `TippList.get_queryset()` to annotate comment counts. Add after the search filter and before the sort:

```python
        # Annotate comment count
        qs = qs.annotate(comment_count=Count("comments"))
```

And pass comment forms in `get_context_data`:

```python
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["current_sort"] = self.request.GET.get("sort", "votes")
        context["search_query"] = self.request.GET.get("q", "")
        context["comment_form"] = forms.TippCommentForm()
        return context
```

- [ ] **Step 4: Add comment URLs to urls.py**

Add to `apps/tipps/urls.py` urlpatterns:

```python
    re_path(
        r"^(?P<pk>-?\d+)/comment/add/$",
        views.TippCommentAdd.as_view(),
        name="tipp_comment_add",
    ),
    re_path(
        r"^comment/(?P<pk>-?\d+)/edit/$",
        views.TippCommentEdit.as_view(),
        name="tipp_comment_edit",
    ),
    re_path(
        r"^comment/(?P<pk>-?\d+)/delete/$",
        views.TippCommentDelete.as_view(),
        name="tipp_comment_delete",
    ),
```

- [ ] **Step 5: Create comment_form.html template**

Create `apps/tipps/templates/tipps/comment_form.html`:

```html
{% extends 'base.html' %}
{% load tabs %}

{% block title %}Kommentar bearbeiten{% endblock %}

{% block navigation %}
    {% activetab 'navigation' 'tipps' %}
    {{ block.super }}
{% endblock %}

{% block content %}
    <div class="page-header">
        <h1>Kommentar bearbeiten</h1>
    </div>

    <form method="POST" class="form-horizontal">{% csrf_token %}
        {% include 'lib/form_loop.html' %}
        <div class="form-actions">
            <button type="submit" class="button button-primary">Speichern</button>
            <a href="{% url 'tipps:tipp_list' %}" class="button">Abbrechen</a>
        </div>
    </form>
{% endblock %}
```

- [ ] **Step 6: Create comment_confirm_delete.html template**

Create `apps/tipps/templates/tipps/comment_confirm_delete.html`:

```html
{% extends 'base.html' %}
{% load tabs %}

{% block title %}Kommentar löschen{% endblock %}

{% block navigation %}
    {% activetab 'navigation' 'tipps' %}
    {{ block.super }}
{% endblock %}

{% block content %}
    <div class="page-header">
        <h1>Kommentar löschen</h1>
    </div>

    <p>Möchtest du wirklich den folgenden Kommentar löschen?</p>

    <ul>
        <li><strong>Erfasst am</strong> {{ object.date|date }}</li>
        <li><strong>Kommentar</strong> {{ object.text }}</li>
    </ul>

    <form method="post">{% csrf_token %}
        <button type="submit" class="btn btn-danger">
            <i class="icon-trash icon-white"></i> Ja, ich bin sicher.
        </button>
    </form>
{% endblock %}
```

- [ ] **Step 7: Add comment section to tipp_list.html**

In `apps/tipps/templates/tipps/tipp_list.html`, add the comment section inside each `<article>` element, after the closing `</div>` of `quote-wrapper` and before the closing `</article>` tag:

```html
          <div class="comments-section">
            <button class="button comment-toggle" onclick="var el=document.getElementById('comments-{{ tipp.pk }}'); el.style.display = el.style.display === 'none' ? 'block' : 'none';">
                {{ tipp.comment_count }} Kommentar{{ tipp.comment_count|pluralize:"e" }}
            </button>
            <div id="comments-{{ tipp.pk }}" style="display:none;">
                {% for comment in tipp.comments.all %}
                    <div class="comment">
                        <p class="comment-meta">
                            {% if comment.author %}
                                <strong>{{ comment.author.name }}</strong>
                            {% else %}
                                <strong>Gelöschter User</strong>
                            {% endif %}
                            — {{ comment.date|date }}
                            {% if comment.author_id == user.pk %}
                                <a href="{% url 'tipps:tipp_comment_edit' comment.pk %}">Bearbeiten</a>
                                <a href="{% url 'tipps:tipp_comment_delete' comment.pk %}">Löschen</a>
                            {% elif user.is_staff %}
                                <a href="{% url 'tipps:tipp_comment_delete' comment.pk %}">Löschen</a>
                            {% endif %}
                        </p>
                        <p>{{ comment.text }}</p>
                    </div>
                {% endfor %}
                {% if user.is_authenticated %}
                    <form method="POST" action="{% url 'tipps:tipp_comment_add' tipp.pk %}" class="comment-form">
                        {% csrf_token %}
                        <textarea name="text" placeholder="Kommentar hinzufügen..." required></textarea>
                        <button type="submit" class="button">Kommentar hinzufügen</button>
                    </form>
                {% endif %}
            </div>
          </div>
```

Note on pluralization: Django's `pluralize` filter with `"e"` argument outputs `""` for count 1 and `"e"` for other counts, giving "1 Kommentar" and "0 Kommentare" / "2 Kommentare".

- [ ] **Step 8: Run tests to verify they pass**

Run:
```bash
docker compose run --rm studentenportal_dev pytest tests/tipps/ -v
```
Expected: All tests PASS.

- [ ] **Step 9: Run full test suite**

Run:
```bash
docker compose run --rm studentenportal_dev pytest tests/ -v
```
Expected: All tests PASS.

- [ ] **Step 10: Commit**

```bash
git add apps/tipps/views.py apps/tipps/urls.py apps/tipps/forms.py apps/tipps/templates/tipps/ tests/tipps/test_views.py
git commit -m "feat: add comment system with add, edit, delete views and toggled display"
```

---

### Task 7: Manual verification in browser

**Files:** None — verification only.

**Interfaces:**
- Consumes: All previous tasks
- Produces: Verified working feature

- [ ] **Step 1: Start dev server if not running**

Run:
```bash
docker compose up -d
```

- [ ] **Step 2: Verify tipps list loads at http://localhost:8000/tipps/**

Check:
- Sort toggle shows "Beliebteste" and "Neueste"
- Search input is present
- Tipps render with markdown (bold, italic, etc.)
- Comment count badge is visible for each tipp

- [ ] **Step 3: Test adding a tipp with EasyMDE**

Go to http://localhost:8000/tipps/add/ (login first). Check:
- EasyMDE editor appears on the description field
- Toolbar has markdown formatting buttons
- Submit creates the tipp and markdown renders correctly in the list

- [ ] **Step 4: Test editing a tipp**

Find your tipp in the list. Check:
- "Bearbeiten" button is visible
- Clicking it opens the form with pre-filled data and EasyMDE
- Submitting updates the tipp

- [ ] **Step 5: Test sorting**

Create multiple tipps with different vote counts. Check:
- "Beliebteste" shows most-voted first
- "Neueste" shows newest first
- Active sort button is highlighted

- [ ] **Step 6: Test search**

Search for a tipp by title and description. Check:
- Results are filtered correctly
- Search term persists in input
- Sort toggle works with search active

- [ ] **Step 7: Test comments**

On a tipp, check:
- Comment count badge shows "0 Kommentare"
- Clicking it reveals the comment section
- Add a comment — count updates to "1 Kommentar"
- Edit your comment — text updates
- Delete your comment — it disappears
- Log in as admin — delete button visible on all comments

- [ ] **Step 8: Test XSS protection**

Add a tipp with description: `<script>alert('xss')</script>`. Check:
- No alert fires
- Script tag is stripped in rendered output
