# Tipps Enhancements Design

**Date:** 2026-09-12
**Scope:** Vote-based sorting, search, markdown rendering + WYSIWYG, edit view, comment system

## 1. Sorting (vote-based with toggle)

**Default ordering:** `-vote_sum` (most votes first), tiebreaker `-date` (newest among equal votes).

**Toggle:** Two links above the list — "Beliebteste" (default, `?sort=votes`) and "Neueste" (`?sort=date`). Active link is visually highlighted.

**Implementation:** The `extend_with_votes()` annotation already provides `upvote_count` and `downvote_count`. Annotate `vote_sum` as `upvote_count - downvote_count` using Django's `F()` expressions, then `.order_by()` based on the `sort` query parameter. Default sort is `-vote_sum, -date`. Date sort is `-date`.

**Files:** `apps/tipps/views.py` (TippList.get_queryset), `apps/tipps/templates/tipps/tipp_list.html`.

## 2. Search

**Input:** Text field above the tipp list, submits as GET with `?q=searchterm`.

**Filter:** `Q(summary__icontains=q) | Q(description__icontains=q)`.

**Behavior:** Preserves sort parameter (`?q=foo&sort=votes`). Empty query shows all tipps. Search term persists in the input field after submission.

**Files:** `apps/tipps/views.py` (TippList.get_queryset), `apps/tipps/templates/tipps/tipp_list.html`.

## 3. Markdown rendering

**Move shared filter:** The `render_markdown` filter currently lives in `apps/events/templatetags/md.py`. Move it to `apps/front/templatetags/md.py` so all apps can use it. Update events templates to load from the new location.

**XSS protection:** The current implementation uses `mark_safe()` on user-generated content, which is an XSS risk. Add `bleach` to sanitize HTML output. Allow safe tags: `p, br, em, strong, ul, ol, li, a, code, pre, blockquote, h1-h6, table, thead, tbody, tr, th, td, hr, img`. Allow `href` on `a` tags and `src`/`alt` on `img` tags.

**Template usage:** Replace `{{ tipp.description }}` with `{{ tipp.description|render_markdown }}` in the list template.

**Files:** `apps/front/templatetags/md.py` (new), `apps/events/templatetags/md.py` (update import or keep as proxy), `apps/tipps/templates/tipps/tipp_list.html`, `requirements/base/requirements.txt` (add bleach).

## 4. WYSIWYG markdown editor (EasyMDE)

**Library:** EasyMDE loaded from CDN (`https://cdn.jsdelivr.net/npm/easymde/dist/easymde.min.css` and `.js`).

**Integration:** In `tipp_form.html`, load EasyMDE CSS in head block and JS at bottom. Initialize with:
```javascript
new EasyMDE({
    element: document.getElementById('id_description'),
    spellChecker: false,
    status: false,
});
```

**Used on:** Tipp add and edit forms (both use `tipp_form.html`).

**Files:** `apps/tipps/templates/tipps/tipp_form.html`.

## 5. Edit view (new)

**View:** `TippEdit` — UpdateView with LoginRequiredMixin. Only the author can edit (check `self.get_object().author == request.user`, return 403 otherwise).

**URL:** `/tipps/<pk>/edit/` → `tipps:tipp_edit`.

**Template:** Reuses `tipp_form.html`. Form pre-populated with existing data.

**UI:** Edit button (pencil icon or "Bearbeiten" text) visible next to delete button when `tipp.author_id == user.pk`.

**Files:** `apps/tipps/views.py`, `apps/tipps/urls.py`, `apps/tipps/templates/tipps/tipp_list.html`.

## 6. Comment system

### 6.1 Model

```python
class TippComment(models.Model):
    tipp = models.ForeignKey(Tipp, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                               null=True, related_name="tipp_comments")
    text = models.TextField(verbose_name="Kommentar")
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["date"]  # oldest first within a tipp

    def __str__(self):
        return f"Comment by {self.author} on Tipp {self.tipp_id}"
```

### 6.2 Views

**TippCommentAdd:** CreateView or POST-only view. Login required. Sets `author = request.user`, `tipp` from URL pk. Redirects back to tipp list (same page, anchored to the tipp).

**TippCommentEdit:** UpdateView. Login required. Only author can edit (`comment.author == request.user`, 403 otherwise). Uses a simple form with just the `text` field.

**TippCommentDelete:** DeleteView. Login required. Author OR admin (`request.user == comment.author or request.user.is_staff`). Redirects back to tipp list.

### 6.3 URLs

```
/tipps/<pk>/comment/add/          → tipps:tipp_comment_add
/tipps/comment/<pk>/edit/         → tipps:tipp_comment_edit
/tipps/comment/<pk>/delete/       → tipps:tipp_comment_delete
```

### 6.4 Template behavior

**Comment count badge:** Each tipp shows a clickable element: `"💬 3 Kommentare"` (or `"💬 0 Kommentare"`). This is a button/link that toggles visibility.

**Hidden by default:** The comment section is wrapped in a container with `style="display:none"`. Clicking the badge toggles it via a small inline JavaScript function (no separate JS file needed — just a toggle on click).

**Comment list:** Inside the toggled container:
- Each comment shows: author name (or "Gelöschter User"), date, text
- Author sees "Bearbeiten" and "Löschen" links on their own comments
- Admin (`user.is_staff`) sees "Löschen" on all comments

**Add comment form:** At the bottom of the comment section, visible only to authenticated users. Inline form with a textarea and submit button. POST to `tipp_comment_add`.

**Edit comment:** Separate page with form (textarea + submit), consistent with project style. Goes to a simple form page, redirects back after save.

**Delete comment:** Confirmation page consistent with `tipp_confirm_delete.html` style.

### 6.5 Admin

Register `TippComment` with `list_display = ("tipp", "author", "date")` and `list_filter = ("date",)`.

### 6.6 Forms

```python
class TippCommentForm(forms.ModelForm):
    class Meta:
        model = TippComment
        fields = ("text",)
```

**Files:** `apps/tipps/models.py`, `apps/tipps/views.py`, `apps/tipps/forms.py`, `apps/tipps/urls.py`, `apps/tipps/admin.py`, `apps/tipps/templates/tipps/tipp_list.html`, new templates for comment edit/delete confirmation.

## 7. Migration

One new migration adding the `TippComment` model.

## 8. Testing

Tests for:
- TippList sorting: default (votes desc, date desc tiebreaker), date sorting
- TippList search: matches summary, matches description, no results
- Markdown rendering: basic markdown converts to HTML, XSS sanitized
- TippEdit: author can edit, non-author gets 403, anonymous redirected to login
- TippCommentAdd: authenticated user can add, anonymous cannot
- TippCommentEdit: author can edit, non-author gets 403
- TippCommentDelete: author can delete, admin can delete, other user gets 403
- Comment count annotation on tipp list

## 9. Dependencies

**New:** `bleach` (HTML sanitization for markdown output).
**Existing:** `markdown` (already installed), EasyMDE (CDN, no package install).
