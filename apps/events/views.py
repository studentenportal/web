import copy
import datetime
from urllib.parse import urlsplit, urlunsplit

import vobject
from dateutil.relativedelta import relativedelta
from django.contrib import messages
from django.contrib.syndication.views import Feed
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect
from django.urls import reverse
from django.views.generic import TemplateView, View
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from apps.events import forms, models
from apps.front.listing import ListingMixin
from apps.front.mixins import LoginRequiredMixin


class Event(DetailView):
    model = models.Event


class EventAdd(LoginRequiredMixin, CreateView):
    model = models.Event
    form_class = forms.EventForm

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.author = self.request.user
        self.object.save()
        messages.add_message(
            self.request,
            messages.SUCCESS,
            'Event "%s" wurde erfolgreich erstellt.' % self.object.summary,
        )
        return HttpResponseRedirect(
            reverse("events:event_detail", args=[self.object.pk])
        )


class EventEdit(LoginRequiredMixin, UpdateView):
    model = models.Event
    form_class = forms.EventForm

    def dispatch(self, request, *args, **kwargs):
        handler = super().dispatch(request, *args, **kwargs)
        # Only allow editing if current user is owner
        if self.object.author != request.user:
            return HttpResponseForbidden("Du darfst keine fremden Events editieren.")
        return handler

    def get_success_url(self):
        return reverse("events:event_detail", args=[self.object.pk])


class EventDelete(LoginRequiredMixin, DeleteView):
    model = models.Event

    def dispatch(self, request, *args, **kwargs):
        handler = super().dispatch(request, *args, **kwargs)
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


def _nth_weekday_of_month(year, month, weekday, n):
    """Find the nth occurrence of a weekday in a given month.

    Args:
        year, month: Target month.
        weekday: 0=Monday ... 6=Sunday.
        n: 1-based occurrence (1st, 2nd, 3rd, ...).

    Returns:
        A date, or None if the nth occurrence doesn't exist.
    """
    import calendar

    first_day, days_in_month = calendar.monthrange(year, month)
    # Find the first occurrence of the weekday
    first_occurrence = 1 + (weekday - first_day) % 7
    target_day = first_occurrence + (n - 1) * 7
    if target_day > days_in_month:
        return None
    return datetime.date(year, month, target_day)


def repeat_dates(start_date, repeat_every, repeat_unit, end_date):
    """Generate recurring dates from start_date to end_date.

    For 'month' and 'year' units, uses weekday-of-month logic
    (e.g., 2nd Tuesday) rather than day-of-month.
    """
    dates = []
    if repeat_unit == "day":
        d = start_date
        while d <= end_date:
            dates.append(d)
            d += datetime.timedelta(days=repeat_every)
    elif repeat_unit == "week":
        d = start_date
        while d <= end_date:
            dates.append(d)
            d += datetime.timedelta(weeks=repeat_every)
    elif repeat_unit == "month":
        weekday = start_date.weekday()
        n = (start_date.day - 1) // 7 + 1  # which occurrence (1st, 2nd, ...)
        if start_date <= end_date:
            dates.append(start_date)
        month_offset = repeat_every
        while True:
            total_months = start_date.year * 12 + (start_date.month - 1) + month_offset
            y, m = divmod(total_months, 12)
            m += 1
            candidate = _nth_weekday_of_month(y, m, weekday, n)
            if candidate is None:
                month_offset += repeat_every
                continue
            if candidate > end_date:
                break
            dates.append(candidate)
            month_offset += repeat_every
    elif repeat_unit == "year":
        weekday = start_date.weekday()
        n = (start_date.day - 1) // 7 + 1
        target_month = start_date.month
        if start_date <= end_date:
            dates.append(start_date)
        year_offset = repeat_every
        while True:
            y = start_date.year + year_offset
            candidate = _nth_weekday_of_month(y, target_month, weekday, n)
            if candidate is None:
                year_offset += repeat_every
                continue
            if candidate > end_date:
                break
            dates.append(candidate)
            year_offset += repeat_every
    return dates


def add_recurring_events(events):
    future = []
    past = []
    for e in events:
        if e.start_date > datetime.date.today():
            future.append(e)
        else:
            past.append(e)
        if (
            e.repeats
            and e.repeat_every is not None
            and e.repeat_every > 0
            and e.repeat_unit is not None
            and e.repeat_ends is not None
        ):
            dates = repeat_dates(
                e.start_date, e.repeat_every, e.repeat_unit, e.repeat_ends
            )
            for date in dates[1:]:
                new_e = copy.copy(e)
                new_e.start_date = date
                new_e.is_recurring_instance = True
                new_e.end_date = (
                    date + (e.end_date - e.start_date)
                    if e.end_date is not None
                    else None
                )
                if date > datetime.date.today():
                    future.append(new_e)
                else:
                    past.append(new_e)
    return sorted(
        future, key=lambda e: (e.start_date, e.start_time or datetime.time.min)
    ), sorted(
        past,
        key=lambda e: (-e.start_date.toordinal(), e.start_time or datetime.time.min),
    )


class EventList(ListingMixin, TemplateView):
    template_name = "events/event_list.html"
    search_fields = ("summary", "description", "location")
    search_placeholder = "Events durchsuchen..."
    past_page_size = 50

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        events = self.apply_search(models.Event.objects.all())
        future, past = add_recurring_events(events)

        context["events_future"] = future
        # TODO: let user input the timeframe
        past_events = [
            e
            for e in past
            if e.start_date > datetime.date.today() - relativedelta(years=10)
        ]
        paginator = Paginator(past_events, self.past_page_size)
        page_obj = paginator.get_page(self.request.GET.get("page", 1))
        context["events_past"] = list(page_obj.object_list)
        context["paginator"] = paginator
        context["page_obj"] = page_obj
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

        future, past = add_recurring_events(models.Event.objects.all())

        for event in reversed(future + past):
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


class EventFeed(Feed):
    title = "Studentenportal Events"
    description = "Neue Events auf studentenportal.ch"
    link = "/events/"

    def items(self):
        return models.Event.objects.filter(
            start_date__gte=datetime.date.today()
        ).order_by("start_date", "start_time")[:20]

    def item_title(self, item):
        return item.summary

    def item_description(self, item):
        if item.location:
            return "%s\nOrt: %s" % (item.description, item.location)
        return item.description

    def item_link(self, item):
        return reverse("events:event_detail", args=[item.pk])

    def item_pubdate(self, item):
        return datetime.datetime.combine(
            item.start_date, item.start_time or datetime.time(0, 0)
        )
