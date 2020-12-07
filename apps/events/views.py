# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import datetime
from dateutil.relativedelta import relativedelta
from urllib.parse import urlsplit, urlunsplit

from django.views.generic import View, TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponse
from django.http import HttpResponseForbidden

import vobject

from apps.events import forms, models
from apps.front.mixins import LoginRequiredMixin


class Event(DetailView):
    model = models.Event


class EventAdd(LoginRequiredMixin, CreateView):
    model = models.Event
    form_class = forms.EventForm

    def form_valid(self, form):
        """Override the form_valid method of the ModelFormMixin to insert
        value of author field. To do this, the form's save() method is
        called with commit=False to be able to edit the new object before
        actually saving it."""
        self.object = form.save(commit=False)
        self.object.author = self.request.user
        self.object.save()
        return super(EventAdd, self).form_valid(form)

    def get_success_url(self):
        messages.add_message(
            self.request,
            messages.SUCCESS,
            'Event "%s" wurde erfolgreich erstellt.' % self.object.summary,
        )
        return reverse("events:event_detail", args=[self.object.pk])


class EventEdit(LoginRequiredMixin, UpdateView):
    model = models.Event
    form_class = forms.EventForm

    def dispatch(self, request, *args, **kwargs):
        handler = super(EventEdit, self).dispatch(request, *args, **kwargs)
        # Only allow editing if current user is owner
        if self.object.author != request.user:
            return HttpResponseForbidden("Du darfst keine fremden Events editieren.")
        return handler

    def get_success_url(self):
        return reverse("events:event_detail", args=[self.object.pk])


class EventDelete(LoginRequiredMixin, DeleteView):
    model = models.Event

    def dispatch(self, request, *args, **kwargs):
        handler = super(EventDelete, self).dispatch(request, *args, **kwargs)
        # Only allow deletion if current user is owner
        if self.object.author != request.user:
            return HttpResponseForbidden("Du darfst keine fremden Events löschen.")
        return handler

    def get_success_url(self):
        messages.add_message(
            self.request,
            messages.SUCCESS,
            'Event "%s" wurde erfolgreich gelöscht.' % self.object.summary,
        )
        return reverse("events:event_list")


class EventList(TemplateView):
    template_name = "events/event_list.html"

    def get_context_data(self, **kwargs):
        model = models.Event
        context = super(EventList, self).get_context_data(**kwargs)
        context["events_future"] = model.objects.filter(
            start_date__gte=datetime.date.today()
        ).order_by("start_date", "start_time")
        context["events_past"] = model.objects.filter(
            start_date__lt=datetime.date.today(),
            start_date__gt=datetime.date.today() - relativedelta(years=2),
        ).order_by("-start_date", "start_time")
        http_url = self.request.build_absolute_uri(reverse("events:event_calendar"))
        context["current_year"] = datetime.date.today().year
        context["webcal_url"] = urlunsplit(urlsplit(http_url)._replace(scheme="webcal"))
        return context


class EventCalendar(View):
    http_method_names = ["get", "head", "options"]

    def get(self, request, *args, **kwargs):
        cal = vobject.iCalendar()
        cal.add("x-wr-calname").value = "Studentenportal Events"
        cal.add("x-wr-timezone").value = "Europe/Zurich"
        for event in models.Event.objects.all():
            vevent = cal.add("vevent")
            vevent.add("summary").value = event.summary
            vevent.add("description").value = event.description
            if event.start_time:
                dtstart = datetime.datetime.combine(event.start_date, event.start_time)
            else:
                dtstart = event.start_date
            vevent.add("dtstart").value = dtstart
            if event.end_date or event.end_time:
                if not event.end_date:
                    dtend = datetime.datetime.combine(event.start_date, event.end_time)
                elif event.end_time:
                    dtend = datetime.datetime.combine(event.end_date, event.end_time)
                else:
                    dtend = datetime.datetime.combine(
                        event.end_date, datetime.time(23, 59, 59)
                    )
                vevent.add("dtend").value = dtend
            if event.author:
                vevent.add("comment").value = "Erfasst von %s" % event.author.name()
        return HttpResponse(cal.serialize(), content_type="text/calendar")
