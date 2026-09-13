from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, Q
from django.urls import reverse
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView
from django.views.generic.list import ListView

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
            self.object.Quote.all(),
            "lecturers_quotevote",
            "quote_id",
            "lecturers_quote",
            self.request.user.pk,
        )

        # Ratings
        ratings = models.LecturerRating.objects.filter(
            lecturer=self.get_object(), user=self.request.user
        )
        ratings_dict = {r.category: r.rating for r in ratings}
        for cat in ["d", "m", "f"]:
            context["rating_%c" % cat] = ratings_dict.get(cat)

        return context


class LecturerList(LoginRequiredMixin, ListView):
    paginate_by = 50
    context_object_name = "lecturers"

    def get_queryset(self):
        queryset = models.Lecturer.real_objects.all()
        query = self.request.GET.get("q", "").strip()
        if query:
            queryset = queryset.filter(
                Q(first_name__icontains=query) | Q(last_name__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        quotecounts = (
            models.Quote.objects.values_list("lecturer")
            .annotate(Count("pk"))
            .order_by()
        )
        context["quotecounts"] = dict(quotecounts)
        return context


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


class QuoteList(LoginRequiredMixin, ListView):
    context_object_name = "quotes"
    paginate_by = 50

    def get_queryset(self):
        return extend_with_votes(
            models.Quote.objects.all(),
            "lecturers_quotevote",
            "quote_id",
            "lecturers_quote",
            self.request.user.pk,
        )


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
