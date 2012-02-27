# coding=utf-8
import datetime
from django.contrib.auth import models as auth_models
from django.contrib import messages
from django.db.models import Count
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseForbidden
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.shortcuts import get_object_or_404
from apps.front.mixins import LoginRequiredMixin
from apps.front import forms
from apps.front import models


class Home(TemplateView):
    template_name = 'front/home.html'


# Auth stuff {{{
class Profile(LoginRequiredMixin, UpdateView):
    form_class = forms.ProfileForm
    template_name = 'front/profile_form.html'

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
# }}}


# Events {{{
class Event(DetailView):
    model = models.Event
    context_object_name = 'event'


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
        messages.add_message(self.request, messages.SUCCESS,
            u'Event "%s" wurde erfolgreich erstellt.' % self.object.summary)
        return reverse('event_detail', args=[self.object.pk])


class EventEdit(LoginRequiredMixin, UpdateView):
    model = models.Event
    form_class = forms.EventForm

    def dispatch(self, request, *args, **kwargs):
        handler = super(EventEdit, self).dispatch(request, *args, **kwargs)
        # Only allow editing if current user is owner
        if self.object.author != request.user:
            return HttpResponseForbidden(u'Du darfst keine fremden Events editieren.')
        return handler

    def get_success_url(self):
        return reverse('event_detail', args=[self.object.pk])


class EventDelete(LoginRequiredMixin, DeleteView):
    model = models.Event
    context_object_name = 'quote'

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
# }}}


# Lecturers {{{
class Lecturer(LoginRequiredMixin, DetailView):
    model = models.Lecturer
    context_object_name = 'lecturer'

    def get_context_data(self, **kwargs):
        context = super(Lecturer, self).get_context_data(**kwargs)
        context['quotes'] = self.object.Quote.all()
        return context


class LecturerList(LoginRequiredMixin, ListView):
    model = models.Lecturer
    context_object_name = 'lecturers'

    def get_context_data(self, **kwargs):
        context = super(LecturerList, self).get_context_data(**kwargs)
        quotecounts = models.Quote.objects.values_list('lecturer').annotate(Count('pk')).order_by()
        context['quotecounts'] = dict(quotecounts)
        return context
# }}}


# Quotes {{{
class QuoteList(LoginRequiredMixin, ListView):
    model = models.Quote
    context_object_name = 'quotes'


class QuoteAdd(LoginRequiredMixin, CreateView):
    model = models.Quote
    form_class = forms.QuoteForm

    def dispatch(self, request, *args, **kwargs):
        try:
            self.lecturer = models.Lecturer.objects.get(pk=kwargs.get('pk'))
        except (ObjectDoesNotExist, ValueError):
            self.lecturer = None
        return super(QuoteAdd, self).dispatch(request, *args, **kwargs)

    def get_form(self, form_class):
        """Add the pk as first argument to the form."""
        return form_class(self.kwargs.get('pk'), **self.get_form_kwargs())

    def get_context_data(self, **kwargs):
        context = super(QuoteAdd, self).get_context_data(**kwargs)
        context['lecturer'] = self.lecturer
        return context

    def form_valid(self, form):
        """Override the form_valid method of the ModelFormMixin to insert
        value of author field. To do this, the form's save() method is
        called with commit=False to be able to edit the new object before
        actually saving it."""
        self.object = form.save(commit=False)
        self.object.author = self.request.user
        self.object.save()
        return super(QuoteAdd, self).form_valid(form)

    def get_success_url(self):
        """Redirect to quotes or lecturer page."""
        messages.add_message(self.request, messages.SUCCESS,
            u'Zitat wurde erfolgreich hinzugefügt.')
        if self.lecturer:
            return reverse('lecturer_detail', args=[self.lecturer.pk])
        return reverse('quote_list')


class QuoteDelete(LoginRequiredMixin, DeleteView):
    model = models.Quote

    def dispatch(self, request, *args, **kwargs):
        handler = super(QuoteDelete, self).dispatch(request, *args, **kwargs)
        # Only allow deletion if current user is owner
        if self.object.author != request.user:
            return HttpResponseForbidden(u'Du darfst keine fremden Quotes löschen.')
        return handler

    def get_success_url(self):
        messages.add_message(self.request, messages.SUCCESS,
            u'Zitat wurde erfolgreich gelöscht.')
        return reverse('quote_list')
# }}}


# Documents {{{
class DocumentcategoryList(ListView):
    model = models.DocumentCategory


class DocumentcategoryAdd(LoginRequiredMixin, CreateView):
    model = models.DocumentCategory

    def get_success_url(self):
        messages.add_message(self.request, messages.SUCCESS,
            u'Modul "%s" wurde erfolgreich hinzugefügt.' % self.object.name)
        return reverse('documentcategory_list')


class DocumentcategoryEdit(LoginRequiredMixin, UpdateView):
    model = models.DocumentCategory


class DocumentcategoryDelete(LoginRequiredMixin, DeleteView):
    model = models.DocumentCategory


class DocumentcategoryMixin(object):
    """Mixin that adds the current documentcategory object to the context.
    Provide the category slug in kwargs['category']."""

    def dispatch(self, request, *args, **kwargs):
        self.category = get_object_or_404(models.DocumentCategory, name__iexact=kwargs['category'])
        return super(DocumentcategoryMixin, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(DocumentcategoryMixin, self).get_context_data(**kwargs)
        context['documentcategory'] = self.category
        return context


class DocumentList(DocumentcategoryMixin, ListView):
    template_name = 'front/document_list.html'
    context_object_name = 'documents'

    def get_queryset(self):
        return models.Document.objects.filter(category=self.category)


class DocumentAdd(LoginRequiredMixin, DocumentcategoryMixin, CreateView):
    model = models.Document
    form_class = forms.DocumentForm

    def form_valid(self, form):
        """Override the form_valid method of the ModelFormMixin to insert
        value of author and category field. To do this, the form's save()
        method is called with commit=False to be able to edit the new
        object before actually saving it."""
        self.object = form.save(commit=False)
        self.object.uploader = self.request.user
        self.object.category = self.category
        self.object.save()
        return super(DocumentAdd, self).form_valid(form)

    def get_success_url(self):
        """Redirect to documentcategory page."""
        messages.add_message(self.request, messages.SUCCESS,
            u'Dokument wurde erfolgreich hinzugefügt.')
        return reverse('document_list', args=[self.category])


class DocumentEdit(LoginRequiredMixin, DocumentcategoryMixin, UpdateView):
    model = models.Document
    form_class = forms.DocumentForm


class DocumentDelete(LoginRequiredMixin, DocumentcategoryMixin, DeleteView):
    model = models.Document
# }}}
