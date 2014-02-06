# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from django.contrib import messages
from django.db.models import Count
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseForbidden
from django.views.generic.edit import CreateView, DeleteView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView

from apps.lecturers import forms, models, helpers
from apps.front.mixins import LoginRequiredMixin


# Lecturers {{{
class Lecturer(LoginRequiredMixin, DetailView):
    model = models.Lecturer
    context_object_name = 'lecturer'

    def get_context_data(self, **kwargs):
        context = super(Lecturer, self).get_context_data(**kwargs)

        # Quotes / QuoteVotes
        context['quotes'] = helpers.extend_quotes_with_votes(
            self.object.Quote.all(),
            self.request.user.pk
        )

        # Ratings
        ratings = models.LecturerRating.objects.filter(
            lecturer=self.get_object(), user=self.request.user)
        ratings_dict = dict([(r.category, r.rating) for r in ratings])
        for cat in ['d', 'm', 'f']:
            context['rating_%c' % cat] = ratings_dict.get(cat)

        return context


class LecturerList(LoginRequiredMixin, ListView):
    queryset = models.Lecturer.real_objects.all()
    context_object_name = 'lecturers'

    def get_context_data(self, **kwargs):
        context = super(LecturerList, self).get_context_data(**kwargs)
        quotecounts = models.Quote.objects.values_list('lecturer').annotate(Count('pk')).order_by()
        context['quotecounts'] = dict(quotecounts)
        return context
# }}}


# Quotes {{{
class QuoteList(LoginRequiredMixin, ListView):
    context_object_name = 'quotes'
    paginate_by = 50

    def get_queryset(self):
        return helpers.extend_quotes_with_votes(
            models.Quote.objects.all(),
            self.request.user.pk
        )


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
        actually saving it. Additionally, directly upvote the quote."""
        self.object = form.save(commit=False)
        is_edit = self.object.pk is not None
        self.object.author = self.request.user
        self.object.save()
        if not is_edit:
            # Automatically upvote own quote
            models.QuoteVote.objects.create(
                user=self.request.user, quote=self.object, vote=True,
            )
        return super(QuoteAdd, self).form_valid(form)

    def get_success_url(self):
        """Redirect to quotes or lecturer page."""
        messages.add_message(self.request, messages.SUCCESS,
            'Zitat wurde erfolgreich hinzugefügt.')
        if self.lecturer:
            return reverse('lecturer_detail', args=[self.lecturer.pk])
        return reverse('quote_list')


class QuoteDelete(LoginRequiredMixin, DeleteView):
    model = models.Quote

    def dispatch(self, request, *args, **kwargs):
        handler = super(QuoteDelete, self).dispatch(request, *args, **kwargs)
        # Only allow deletion if current user is owner
        if self.object.author != request.user:
            return HttpResponseForbidden('Du darfst keine fremden Quotes löschen.')
        return handler

    def get_success_url(self):
        messages.add_message(self.request, messages.SUCCESS,
            'Zitat wurde erfolgreich gelöscht.')
        return reverse('quote_list')
# }}}
