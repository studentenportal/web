# coding=utf-8
import datetime
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseForbidden
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.utils.decorators import method_decorator
from apps.front.decorators import render_to
from apps.front import forms
from apps.front import models


@render_to('home.html')
def home(request):
    return {}


@login_required
@render_to('profile.html')
def profile(request):
    profile_form = forms.ProfileForm(initial={'username': 'danilo'})
    return {
        'form': profile_form,
    }


class Event(DetailView):
    model = models.Event
    context_object_name = 'event'


class EventAdd(CreateView):
    model = models.Event
    form_class = forms.EventForm

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(EventAdd, self).dispatch(*args, **kwargs)

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
        messages.add_message(self.request, messages.SUCCESS,
            u'Event "%s" wurde erfolgreich erstellt.' % self.object.summary)
        return reverse('event_detail', args=[self.object.pk])


class EventEdit(UpdateView):
    model = models.Event
    form_class = forms.EventForm

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        handler = super(EventEdit, self).dispatch(request, *args, **kwargs)
        # Only allow editing if current user is owner
        if self.object.author != request.user:
            return HttpResponseForbidden(u'Du darfst keine fremden Events editieren.')
        return handler

    def get_success_url(self):
        return reverse('event_detail', args=[self.object.pk])


class EventDelete(DeleteView):
    model = models.Event

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        handler = super(EventDelete, self).dispatch(request, *args, **kwargs)
        # Only allow deletion if current user is owner
        if self.object.author != request.user:
            return HttpResponseForbidden(u'Du darfst keine fremden Events löschen.')
        return handler

    def get_success_url(self):
        messages.add_message(self.request, messages.SUCCESS,
            u'Event "%s" wurde erfolgreich gelöscht.' % self.object.summary)
        return reverse('event_list')


class EventList(ListView):
    queryset = models.Event.objects \
               .filter(start_date__gte=datetime.date.today()) \
               .order_by('start_date', 'start_time')
    context_object_name = 'events'


@login_required
@render_to('lecturers.html')
def lecturers(request):
    return {
        'lecturers': (lecturers[::2], lecturers[1::2]),
    }


class DocumentCategories(ListView):
    model = models.DocumentCategory


class DocumentCategory(ListView):
    def get_queryset(self):
        category = self.kwargs.get('category')
        return models.DocumentCategory.objects.get(name__iexact=category).Document.all()
