# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import datetime

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db.models import Count
from django.urls import reverse
from django.views.generic import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView

from apps.documents import models as document_models
from apps.events import models as event_models
from apps.front.mixins import LoginRequiredMixin
from apps.lecturers import models as lecturer_models

from . import forms, models


class Home(TemplateView):
    template_name = "front/home.html"

    def get_context_data(self, **kwargs):
        context = super(Home, self).get_context_data(**kwargs)
        context["events_future"] = event_models.Event.objects.filter(
            start_date__gte=datetime.date.today()
        ).order_by("start_date", "start_time")
        return context


class Profile(LoginRequiredMixin, UpdateView):
    form_class = forms.ProfileForm
    template_name = "front/profile_form.html"

    def get_object(self, queryset=None):
        """Gets the current user object."""
        assert self.request.user, "request.user is empty."
        return self.request.user

    def get_success_url(self):
        messages.add_message(
            self.request, messages.SUCCESS, "Profil wurde erfolgreich aktualisiert."
        )
        return reverse("profile")


class User(LoginRequiredMixin, DetailView):
    model = get_user_model()
    template_name = "front/user_detail.html"

    def get_context_data(self, **kwargs):
        context = super(User, self).get_context_data(**kwargs)
        user = self.get_object()
        context["lecturerratings"] = (
            user.LecturerRating.values_list("lecturer").distinct().count()
        )
        if self.request.user.is_authenticated:
            ratings = document_models.DocumentRating.objects.filter(user=user)
            context["ratings"] = dict([(r.document.pk, r.rating) for r in ratings])
        return context


class Stats(LoginRequiredMixin, TemplateView):
    template_name = "front/stats.html"

    def get_context_data(self, **kwargs):
        context = super(Stats, self).get_context_data(**kwargs)

        # Lecturers
        base_query = "SELECT lecturer_id AS id \
                      FROM lecturers_lecturerrating \
                      WHERE category = '%c' \
                      GROUP BY lecturer_id HAVING COUNT(id) > 5"
        base_query_top = base_query + " ORDER BY AVG(rating) DESC, COUNT(id) DESC"
        base_query_flop = base_query + " ORDER BY AVG(rating) ASC, COUNT(id) DESC"

        def fetchfirst(queryset):
            try:
                return queryset[0]
            except IndexError:
                return None

        context["lecturer_top_d"] = fetchfirst(
            lecturer_models.Lecturer.objects.raw(base_query_top % "d")
        )
        context["lecturer_top_m"] = fetchfirst(
            lecturer_models.Lecturer.objects.raw(base_query_top % "m")
        )
        context["lecturer_top_f"] = fetchfirst(
            lecturer_models.Lecturer.objects.raw(base_query_top % "f")
        )
        context["lecturer_flop_d"] = fetchfirst(
            lecturer_models.Lecturer.objects.raw(base_query_flop % "d")
        )
        context["lecturer_flop_m"] = fetchfirst(
            lecturer_models.Lecturer.objects.raw(base_query_flop % "m")
        )
        context["lecturer_flop_f"] = fetchfirst(
            lecturer_models.Lecturer.objects.raw(base_query_flop % "f")
        )

        context["lecturer_quotes"] = lecturer_models.Lecturer.objects.annotate(
            quotes_count=Count("Quote")
        ).order_by("-quotes_count")[:3]

        # Users
        context["user_topratings"] = fetchfirst(
            models.User.objects.raw(
                """
                        SELECT u.id AS id, COUNT(DISTINCT lr.lecturer_id) AS lrcount
                        FROM front_user u
                        JOIN lecturers_lecturerrating lr
                            ON u.id = lr.user_id
                        GROUP BY u.id
                        ORDER BY lrcount DESC"""
            )
        )
        context["user_topuploads"] = fetchfirst(
            models.User.objects.exclude(username="spimport")
            .annotate(uploads_count=Count("Document"))
            .order_by("-uploads_count")
        )
        context["user_topevents"] = fetchfirst(
            models.User.objects.annotate(events_count=Count("Event")).order_by(
                "-events_count"
            )
        )
        context["user_topquotes"] = fetchfirst(
            models.User.objects.exclude(username="spimport")
            .annotate(quotes_count=Count("Quote"))
            .order_by("-quotes_count")
        )

        return context
