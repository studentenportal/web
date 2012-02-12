# coding=utf-8
import datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth import models as auth_models
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseForbidden
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.utils.decorators import method_decorator
from apps.front import forms
from apps.front import models


class Home(TemplateView):
    template_name = 'front/home.html'


class Profile(UpdateView):
    form_class = forms.ProfileForm
    template_name = 'front/profile_form.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(Profile, self).dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        """Gets the current user object."""
        assert self.request.user, u'request.user is empty.'
        return self.request.user

    def get_success_url(self):
        messages.add_message(self.request, messages.SUCCESS,
            u'Profil wurde erfolgreich aktualisiert.')
        return reverse('profile')


class User(DetailView):
    model = auth_models.User
    template_name = 'front/user_detail.html'


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


class EventList(TemplateView):
    template_name = 'front/event_list.html'

    def get_context_data(self, **kwargs):
        model = models.Event
        context = super(EventList, self).get_context_data(**kwargs)
        context['events_future'] = model.objects \
               .filter(start_date__gte=datetime.date.today()) \
               .order_by('start_date', 'start_time')
        context['events_past'] = model.objects \
               .filter(start_date__lt=datetime.date.today()) \
               .order_by('-start_date', 'start_time')
        return context


class LecturerList(ListView):
    model = models.Lecturer

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(LecturerList, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        # TODO do this in the frontend
        context = super(LecturerList, self).get_context_data(**kwargs)
        context['lecturers'] = (context['object_list'][::2],
                                context['object_list'][1::2])
        return context


class DocumentCategories(ListView):
    model = models.DocumentCategory


class DocumentCategory(ListView):
    def get_queryset(self):
        category = self.kwargs.get('category')
        return models.DocumentCategory.objects.get(name__iexact=category).Document.all()
