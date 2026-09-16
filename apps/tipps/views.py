from django.contrib import messages
from django.db.models import Count, Q
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic.edit import CreateView, DeleteView, UpdateView
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

        # Annotate comment count and prefetch comments to avoid N+1 queries
        qs = qs.annotate(comment_count=Count("comments")).prefetch_related(
            "comments", "comments__author"
        )

        # Sort
        sort = self.request.GET.get("sort", "votes")
        if sort == "date":
            qs = qs.order_by("-date")
        else:
            qs = qs.extra(
                select={
                    "vote_sum_sort": (
                        "(SELECT COUNT(*) FROM tipps_tippvote"
                        " WHERE tipps_tippvote.tipp_id = tipps_tipp.id AND vote = 't')"
                        " - "
                        "(SELECT COUNT(*) FROM tipps_tippvote"
                        " WHERE tipps_tippvote.tipp_id = tipps_tipp.id AND vote = 'f')"
                    )
                },
                order_by=["-vote_sum_sort", "-date"],
            )

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["current_sort"] = self.request.GET.get("sort", "votes")
        context["search_query"] = self.request.GET.get("q", "").strip()
        context["comment_form"] = forms.TippCommentForm()
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


class TippEdit(LoginRequiredMixin, UpdateView):
    model = models.Tipp
    form_class = forms.TippForm
    template_name = "tipps/tipp_form.html"

    def get_object(self, queryset=None):
        if not hasattr(self, "_object"):
            self._object = super().get_object(queryset)
        return self._object

    def get(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return HttpResponseForbidden("Du darfst keine fremden Tipps bearbeiten.")
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return HttpResponseForbidden("Du darfst keine fremden Tipps bearbeiten.")
        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        messages.add_message(
            self.request,
            messages.SUCCESS,
            'Tipp "%s" wurde erfolgreich aktualisiert.' % self.object.summary,
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

    def get_object(self, queryset=None):
        if not hasattr(self, "_object"):
            self._object = super().get_object(queryset)
        return self._object

    def get(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return HttpResponseForbidden("Du darfst keine fremden Kommentare bearbeiten.")
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return HttpResponseForbidden("Du darfst keine fremden Kommentare bearbeiten.")
        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        messages.add_message(
            self.request, messages.SUCCESS, "Kommentar wurde aktualisiert."
        )
        return reverse("tipps:tipp_list")


class TippCommentDelete(LoginRequiredMixin, DeleteView):
    model = models.TippComment
    template_name = "tipps/comment_confirm_delete.html"

    def get_object(self, queryset=None):
        if not hasattr(self, "_object"):
            self._object = super().get_object(queryset)
        return self._object

    def get(self, request, *args, **kwargs):
        comment = self.get_object()
        if comment.author != request.user and not request.user.is_staff:
            return HttpResponseForbidden("Du darfst keine fremden Kommentare löschen.")
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        comment = self.get_object()
        if comment.author != request.user and not request.user.is_staff:
            return HttpResponseForbidden("Du darfst keine fremden Kommentare löschen.")
        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        messages.add_message(
            self.request, messages.SUCCESS, "Kommentar wurde gelöscht."
        )
        return reverse("tipps:tipp_list")
