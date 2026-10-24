import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.db.models import Count
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import FormView, TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView
from registration.models import RegistrationProfile

from apps.documents import models as document_models
from apps.events import models as event_models
from apps.events.views import add_recurring_events
from apps.front.mixins import LoginRequiredMixin
from apps.lecturers import models as lecturer_models

from . import forms, models


class Home(TemplateView):
    template_name = "front/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        events_future, _ = add_recurring_events(event_models.Event.objects.all())
        context["events_future"] = events_future
        return context


class Datenschutz(TemplateView):
    template_name = "front/datenschutz.html"


def send_email_change_notification(user, old_email, new_email):
    """Confirm by e-mail that the user's main e-mail address was changed.

    The old address is informed as well, so that a legitimate user notices
    if someone else changes the e-mail of their account.
    """
    context = {
        "user": user,
        "old_email": old_email,
        "new_email": new_email,
    }
    subject = render_to_string("front/email_change_notice_subject.txt", context)
    subject = "".join(subject.splitlines())
    body = render_to_string("front/email_change_notice.txt", context)
    recipients = [new_email]
    if old_email and old_email != new_email:
        recipients.append(old_email)
    send_mail(
        subject,
        body,
        settings.DEFAULT_FROM_EMAIL,
        recipients,
        fail_silently=True,
    )


class Profile(LoginRequiredMixin, UpdateView):
    form_class = forms.ProfileForm
    template_name = "front/profile_form.html"

    def get_object(self, queryset=None):
        """Gets the current user object.

        The current e-mail is captured here, because the form overwrites
        ``self.object.email`` already during validation
        (ModelForm.construct_instance).
        """
        assert self.request.user, "request.user is empty."
        self.old_email = self.request.user.email
        return self.request.user

    def form_valid(self, form):
        self.email_changed = form.cleaned_data["email"] != self.old_email
        response = super().form_valid(form)
        if self.email_changed:
            send_email_change_notification(
                self.object, self.old_email, self.object.email
            )
        return response

    def get_success_url(self):
        if getattr(self, "email_changed", False):
            messages.add_message(
                self.request,
                messages.SUCCESS,
                'Deine E-Mail-Adresse wurde auf "%s" geändert.' % self.object.email,
            )
        else:
            messages.add_message(
                self.request,
                messages.SUCCESS,
                "Profil wurde erfolgreich aktualisiert.",
            )
        return reverse("profile")


class User(LoginRequiredMixin, DetailView):
    model = get_user_model()
    template_name = "front/user_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        context["lecturerratings"] = (
            user.LecturerRating.values_list("lecturer").distinct().count()
        )
        if self.request.user.is_authenticated:
            ratings = document_models.DocumentRating.objects.filter(user=user)
            context["ratings"] = {r.document.pk: r.rating for r in ratings}
        # the logged in user, not the viewed one, accessed as "object"
        context["user"] = self.request.user
        return context


class ResendActivation(FormView):
    form_class = forms.ResendActivationForm
    template_name = "registration/resend_activation_form.html"
    success_url = reverse_lazy("resend_activation_complete")

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        site = get_current_site(self.request)
        try:
            profile = RegistrationProfile.objects.get(user__email__iexact=email)
        except (
            RegistrationProfile.DoesNotExist,
            RegistrationProfile.MultipleObjectsReturned,
        ):
            # Don't reveal whether the email exists
            return super().form_valid(form)

        if profile.activated:
            return super().form_valid(form)

        # Always regenerate the key and resend — even if expired
        if profile.activation_key_expired():
            # Key validity is anchored on user.date_joined, so refresh it to
            # give the new key a full activation window
            profile.user.date_joined = timezone.now()
            profile.user.save()
        profile.create_new_activation_key()
        profile.send_activation_email(site, self.request)
        return super().form_valid(form)


class ResendActivationComplete(TemplateView):
    template_name = "registration/resend_activation_complete.html"


class ConfirmActive(TemplateView):
    """Confirmation link for inactive users, sent by `notify_inactive_users`.

    No login required: the (unguessable) token in the URL is the proof that
    the user got the e-mail.
    """

    template_name = "front/inactivity_confirmed.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        notice = models.InactivityNotice.objects.filter(token=kwargs["token"]).first()
        confirmed = False
        if notice is not None and not notice.is_confirmed:
            notice.confirmed_at = timezone.now()
            notice.save(update_fields=["confirmed_at"])
            confirmed = True
        context["confirmed"] = confirmed
        return context


class Stats(LoginRequiredMixin, TemplateView):
    template_name = "front/stats.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

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
        context["user_topratings"] = fetchfirst(models.User.objects.raw("""
                        SELECT u.id AS id, COUNT(DISTINCT lr.lecturer_id) AS lrcount
                        FROM front_user u
                        JOIN lecturers_lecturerrating lr
                            ON u.id = lr.user_id
                        GROUP BY u.id
                        ORDER BY lrcount DESC"""))
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
