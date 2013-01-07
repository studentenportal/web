# coding=utf-8
import datetime
import unicodedata
from urlparse import urlsplit, urlunsplit
from django.contrib.auth import models as auth_models
from django.contrib import messages
from django.db.models import Count
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.http import HttpResponse
from django.http import HttpResponseForbidden, HttpResponseServerError, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View, TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.edit import SingleObjectMixin
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.utils.decorators import method_decorator
from django.shortcuts import redirect, get_object_or_404, render
from django.template.defaultfilters import slugify
from sendfile import sendfile
import vobject
from apps.front.mixins import LoginRequiredMixin
from apps.front import forms, models, helpers


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


class User(LoginRequiredMixin, DetailView):
    model = auth_models.User
    template_name = 'front/user_detail.html'

    def get_context_data(self, **kwargs):
        context = super(User, self).get_context_data(**kwargs)
        user = self.get_object()
        context['lecturerratings'] = user.LecturerRating. \
                values_list('lecturer').distinct().count()
        return context
# }}}


# Events {{{
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
        http_url = self.request.build_absolute_uri(reverse('event_calendar'))
        context['webcal_url'] = urlunsplit(urlsplit(http_url)._replace(scheme='webcal'))
        return context


class EventCalendar(View):

    http_method_names = ['get', 'head', 'options']

    def get(self, request, *args, **kwargs):
        cal = vobject.iCalendar()
        cal.add('x-wr-calname').value = 'Studentenportal Events'
        cal.add('x-wr-timezone').value = 'Europe/Zurich'
        for event in models.Event.objects.all():
            vevent = cal.add('vevent')
            vevent.add('summary').value = event.summary
            vevent.add('description').value = event.description
            if event.start_time:
                dtstart = datetime.datetime.combine(event.start_date, event.start_time)
            else:
                dtstart = event.start_date
            vevent.add('dtstart').value = dtstart
            if event.end_date or event.end_time:
                if not event.end_date:
                    dtend = datetime.datetime.combine(event.start_date, event.end_time)
                elif event.end_time:
                    dtend = datetime.datetime.combine(event.end_date, event.end_time)
                else:
                    dtend = event.end_date
                vevent.add('dtend').value = dtend
            if event.author:
                vevent.add('comment').value = 'Erfasst von %s' % event.author.name()
        return HttpResponse(cal.serialize(), content_type='text/calendar')
# }}}


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
    form_class = forms.DocumentCategoryForm

    def get_success_url(self):
        messages.add_message(self.request, messages.SUCCESS,
            u'Modul "%s" wurde erfolgreich hinzugefügt.' % self.object.name)
        return reverse('documentcategory_list')


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

    def get_context_data(self, **kwargs):
        context = super(DocumentList, self).get_context_data(**kwargs)
        if self.request.user.is_authenticated():
            ratings = models.DocumentRating.objects.filter(user=self.request.user)
            context['ratings'] = dict([(r.document.pk, r.rating) for r in ratings])
        return context


class DocumentDownload(View):
    def get(self, request, *args, **kwargs):
        # Get document or raise HTTP404
        doc = get_object_or_404(models.Document, pk=self.kwargs.get('pk'))
        # If document isn't a summary, require login
        if doc.dtype != doc.DTypes.SUMMARY:
            if not self.request.user.is_authenticated():
                return redirect('%s?next=%s' % (
                        reverse('auth_login'),
                        reverse('document_list', kwargs={'category': slugify(doc.category.name)})
                    ))
        # Log download
        ip = helpers.get_client_ip(request)
        timerange = datetime.datetime.now() - datetime.timedelta(1)
        filters = {'document': doc, 'ip': ip, 'timestamp__gt': timerange}
        if not models.DocumentDownload.objects.filter(**filters).exists():
            models.DocumentDownload.objects.create(document=doc, ip=ip)
        # Serve file
        filename = unicodedata.normalize('NFKD', doc.original_filename).encode('us-ascii', 'ignore')
        attachment = not filename.endswith('.pdf')
        return sendfile(request, doc.document.path,
                attachment=attachment, attachment_filename=filename)


class DocumentAdd(LoginRequiredMixin, DocumentcategoryMixin, CreateView):
    model = models.Document
    form_class = forms.DocumentAddForm

    def __init__(self, *args, **kwargs):
        super(DocumentAdd, self).__init__(*args, **kwargs)

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
    form_class = forms.DocumentEditForm

    def dispatch(self, request, *args, **kwargs):
        handler = super(DocumentEdit, self).dispatch(request, *args, **kwargs)
        # Only allow editing if current user is owner
        if self.object.uploader != request.user:
            return HttpResponseForbidden(u'Du darfst keine fremden Uploads editieren.')
        return handler

    def get_success_url(self):
        """Redirect to documentcategory page."""
        messages.add_message(self.request, messages.SUCCESS,
            u'Dokument wurde erfolgreich aktualisiert.')
        return reverse('document_list', args=[self.category])


class DocumentDelete(LoginRequiredMixin, DocumentcategoryMixin, DeleteView):
    model = models.Document

    def get_success_url(self):
        """Redirect to documentcategory page."""
        messages.add_message(self.request, messages.SUCCESS,
            u'Dokument wurde erfolgreich gelöscht.')
        return reverse('document_list', args=[self.category])


class DocumentRate(LoginRequiredMixin, SingleObjectMixin, View):
    model = models.Document
    http_method_names = ['post']

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(DocumentRate, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Create or update the document rating."""
        score = request.POST.get('score')
        if not score:
            return HttpResponseServerError(u'Required argument missing')
        params = {  # Prepare keyword-arguments that identify the rating object
            'user': request.user,
            'document': self.get_object(),
        }
        try:
            rating = models.DocumentRating.objects.get(**params)
        except ObjectDoesNotExist:
            rating = models.DocumentRating(**params)
        rating.rating = score
        try:
            rating.full_clean()  # validation
        except ValidationError:
            return HttpResponseServerError(u'Validierungsfehler')
        rating.save()
        return HttpResponse(u'Bewertung wurde aktualisiert.')


def document_rating(request, category, pk):
    """AJAX view that returns the document_rating_summary block. This is used
    to update the text after changing a rating via JavaScript."""
    if not request.is_ajax():
        return HttpResponseBadRequest(u'XMLHttpRequest expected.')
    if not request.user.is_authenticated():
        return HttpResponseForbidden(u'Login required')
    template = 'front/blocks/document_rating_summary.html'
    context = {'doc': get_object_or_404(models.Document, pk=pk, category__name=category)}
    return render(request, template, context, content_type='text/plain')
# }}}


# Stats {{{
class Stats(LoginRequiredMixin, TemplateView):
    template_name = 'front/stats.html'

    def get_context_data(self, **kwargs):
        context = super(Stats, self).get_context_data(**kwargs)

        # Lecturers
        base_query = "SELECT lecturer_id AS id \
                      FROM front_lecturerrating \
                      WHERE category = '%c' \
                      GROUP BY lecturer_id HAVING COUNT(id) > 5"
        base_query_top = base_query + " ORDER BY AVG(rating) DESC, COUNT(id) DESC"
        base_query_flop = base_query + " ORDER BY AVG(rating) ASC, COUNT(id) DESC"

        def fetchfirst(queryset):
            try:
                return queryset[0]
            except IndexError:
                return None

        context['lecturer_top_d'] = fetchfirst(models.Lecturer.objects.raw(base_query_top % 'd'))
        context['lecturer_top_m'] = fetchfirst(models.Lecturer.objects.raw(base_query_top % 'm'))
        context['lecturer_top_f'] = fetchfirst(models.Lecturer.objects.raw(base_query_top % 'f'))
        context['lecturer_flop_d'] = fetchfirst(models.Lecturer.objects.raw(base_query_flop % 'd'))
        context['lecturer_flop_m'] = fetchfirst(models.Lecturer.objects.raw(base_query_flop % 'm'))
        context['lecturer_flop_f'] = fetchfirst(models.Lecturer.objects.raw(base_query_flop % 'f'))

        context['lecturer_quotes'] = models.Lecturer.objects.annotate(quotes_count=Count('Quote')).order_by('-quotes_count')[:3]

        # Users
        context['user_topratings'] = fetchfirst(
                models.User.objects.raw('''
                        SELECT u.id AS id, COUNT(DISTINCT lr.lecturer_id) AS lrcount
                        FROM auth_user u
                        JOIN front_lecturerrating lr
                            ON u.id = lr.user_id
                        GROUP BY u.id
                        ORDER BY lrcount DESC'''))
        context['user_topuploads'] = fetchfirst(
                models.User.objects
                        .exclude(username=u'spimport')
                        .annotate(uploads_count=Count('Document'))
                        .order_by('-uploads_count'))
        context['user_topevents'] = fetchfirst(
                models.User.objects
                        .annotate(events_count=Count('Event'))
                        .order_by('-events_count'))
        context['user_topquotes'] = fetchfirst(
                models.User.objects
                        .exclude(username=u'spimport')
                        .annotate(quotes_count=Count('Quote'))
                        .order_by('-quotes_count'))

        return context
# }}}
