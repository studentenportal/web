from django.contrib import messages
from django.contrib.syndication.views import Feed
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, F
from django.urls import reverse
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView
from django.views.generic.list import ListView

from apps.front.listing import ListingMixin
from apps.front.mixins import (
    AutoUpvoteCreateMixin,
    LoginRequiredMixin,
    OwnerDeleteMixin,
)
from apps.front.voting import extend_with_votes
from apps.lecturers import forms, models


class Lecturer(LoginRequiredMixin, DetailView):
    model = models.Lecturer
    context_object_name = "lecturer"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Quotes / QuoteVotes
        context["quotes"] = extend_with_votes(
            self.object.Quote.all(), models.QuoteVote, "quote", self.request.user.pk
        )

        # Ratings
        ratings = models.LecturerRating.objects.filter(
            lecturer=self.get_object(), user=self.request.user
        )
        ratings_dict = {r.category: r.rating for r in ratings}
        for cat in ["d", "m", "f"]:
            context["rating_%c" % cat] = ratings_dict.get(cat)

        return context


class LecturerList(LoginRequiredMixin, ListingMixin, ListView):
    context_object_name = "lecturers"
    search_fields = ("first_name", "last_name")
    search_placeholder = "Dozent suchen..."
    sort_options = {
        "name": {"label": "Name", "order_by": ["last_name", "first_name"]},
        "quotes": {"label": "Zitate", "order_by": ["-quote_count", "last_name"]},
    }

    def get_base_queryset(self):
        return models.Lecturer.real_objects.all().annotate(quote_count=Count("Quote"))


class LecturerAdd(LoginRequiredMixin, CreateView):
    model = models.Lecturer
    form_class = forms.LecturerForm

    def get_success_url(self):
        messages.add_message(
            self.request,
            messages.SUCCESS,
            'Dozent "%s" wurde erfolgreich hinzugefügt.' % self.object.name,
        )
        return reverse("lecturers:lecturer_list")


class QuoteList(LoginRequiredMixin, ListingMixin, ListView):
    context_object_name = "quotes"
    search_fields = (
        "quote",
        "comment",
        "lecturer__first_name",
        "lecturer__last_name",
    )
    search_placeholder = "Zitate durchsuchen..."
    sort_options = {
        "date": {"label": "Neueste", "order_by": ["-date"]},
        "votes": {
            "label": "Beliebteste",
            "order_by": [-(F("upvote_count") - F("downvote_count")), "-date"],
        },
    }
    filter_options = {"lecturer": "lecturer"}

    def get_base_queryset(self):
        return extend_with_votes(
            models.Quote.objects.all(), models.QuoteVote, "quote", self.request.user.pk
        )

    def get_filter_choices(self):
        lecturers = models.Lecturer.real_objects.values_list(
            "pk", "last_name", "first_name"
        ).order_by("last_name", "first_name")
        return {
            "lecturer": [
                (pk, ("%s %s" % (last_name, first_name)).strip())
                for pk, last_name, first_name in lecturers
            ]
        }


class QuoteAdd(LoginRequiredMixin, AutoUpvoteCreateMixin, CreateView):
    model = models.Quote
    form_class = forms.QuoteForm
    vote_model = models.QuoteVote
    item_fk_name = "quote"

    def dispatch(self, request, *args, **kwargs):
        try:
            self.lecturer = models.Lecturer.objects.get(pk=kwargs.get("pk"))
        except (ObjectDoesNotExist, ValueError):
            self.lecturer = None
        return super().dispatch(request, *args, **kwargs)

    def get_form(self, form_class=form_class):
        """Add the pk as first argument to the form."""
        return form_class(self.kwargs.get("pk"), **self.get_form_kwargs())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["lecturer"] = self.lecturer
        return context

    def get_success_url(self):
        """Redirect to quotes or lecturer page."""
        messages.add_message(
            self.request, messages.SUCCESS, "Zitat wurde erfolgreich hinzugefügt."
        )
        from apps.front.message_levels import EVENT

        messages.add_message(self.request, EVENT, "quote_add")
        if self.lecturer:
            return reverse("lecturers:lecturer_detail", args=[self.lecturer.pk])
        return reverse("lecturers:quote_list")


class QuoteDelete(LoginRequiredMixin, OwnerDeleteMixin, DeleteView):
    model = models.Quote
    forbidden_message = "Du darfst keine fremden Quotes löschen."
    success_message = "Zitat wurde erfolgreich gelöscht."
    event_name = "quote_delete"
    success_url_name = "lecturers:quote_list"


class QuoteFeed(Feed):
    title = "Studentenportal Zitate"
    description = "Dozenten-Zitate auf studentenportal.ch"
    link = "/zitate/"

    def items(self):
        return models.Quote.objects.all().order_by("-date")[:20]

    def item_title(self, item):
        quote = " ".join(item.quote.split())
        if len(quote) > 60:
            return quote[:57].rstrip() + "..."
        return quote

    def item_description(self, item):
        parts = [item.quote.strip()]
        if item.comment:
            parts.append("Bemerkung: %s" % item.comment.strip())
        parts.append("von %s" % item.lecturer.name())
        return "\n\n".join(parts)

    def item_link(self, item):
        return "%s#quote-%d" % (reverse("lecturers:quote_list"), item.pk)

    def item_pubdate(self, item):
        return item.date
