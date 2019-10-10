# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import os
import subprocess
import datetime
import unicodedata
from collections import defaultdict
import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.syndication.views import Feed
from django.db.models import Count
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.mail import send_mail
from django.http import HttpResponse
from django.http import HttpResponseForbidden, HttpResponseServerError, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View, TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.edit import SingleObjectMixin, FormView
from django.views.generic.list import ListView
from django.utils.decorators import method_decorator
from django.shortcuts import redirect, get_object_or_404, render
from django.template.defaultfilters import slugify

from sendfile import sendfile

from . import models, forms, helpers
from apps.front.mixins import LoginRequiredMixin
from apps.front.message_levels import EVENT


logger = logging.getLogger(__name__)


class DocumentcategoryList(TemplateView):
    template_name = 'documents/documentcategory_list.html'

    def get_context_data(self, **kwargs):
        context = super(DocumentcategoryList, self).get_context_data(**kwargs)

        # Get all categories
        categories = list(models.DocumentCategory.objects.all()
                          .prefetch_related('lecturers')
                          .prefetch_related('courses'))

        # To reduce number of queries, prefetch aggregated count values from the
        # document model. The query returns the count for each (category, dtype) pair.
        category_counts = models.Document.objects.values('category', 'dtype') \
                                .order_by().annotate(count=Count('dtype'))

        # Create counts dictionary ({category_id: {dtype: count, dtype: count, ...}})
        counts = defaultdict(lambda: defaultdict(int))
        for item in category_counts:
            category = item['category']
            dtype = item['dtype']
            counts[category][dtype] = item['count']

        # Add counts to category objects
        simplecounts = defaultdict(dict)
        empty_categories = []
        nonempty_categories = []
        for c in categories:
            d = simplecounts[c.pk]
            d['summary'] = counts[c.pk][models.Document.DTypes.SUMMARY]
            d['exam'] = counts[c.pk][models.Document.DTypes.EXAM]
            d['other'] = counts[c.pk][models.Document.DTypes.SOFTWARE] + \
                         counts[c.pk][models.Document.DTypes.LEARNING_AID] + \
                         counts[c.pk][models.Document.DTypes.ATTESTATION]
            d['total'] = sum(d.values())

            # Sort by category activity
            if d['total'] == 0:
                empty_categories.append(c)
            else:
                nonempty_categories.append(c)

        context['categories'] = nonempty_categories + empty_categories
        context['counts'] = simplecounts
        return context


class DocumentcategoryAdd(LoginRequiredMixin, CreateView):
    model = models.DocumentCategory
    form_class = forms.DocumentCategoryForm

    def get_success_url(self):
        messages.add_message(self.request, messages.SUCCESS,
            'Modul "%s" wurde erfolgreich hinzugefügt.' % self.object.name)
        return reverse('documents:documentcategory_list')


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
    template_name = 'documents/document_list.html'
    context_object_name = 'documents'

    def get_queryset(self):
        return models.Document.objects.filter(category=self.category)

    def get_context_data(self, **kwargs):
        context = super(DocumentList, self).get_context_data(**kwargs)
        if self.request.user.is_authenticated():
            ratings = models.DocumentRating.objects.filter(user=self.request.user)
            context['ratings'] = dict([(r.document.pk, r.rating) for r in ratings])
        return context


class DocumentFeed(Feed):

    def get_object(self, request, *args, **kwargs):
        return get_object_or_404(models.DocumentCategory, name__iexact=kwargs['category'])

    def title(self, obj):
        return obj.name

    def link(self, obj):
        return reverse('documents:document_feed', kwargs={'category': slugify(obj.name)})

    def item_link(self, item):
        return reverse('documents:document_download',
                kwargs={'category': slugify(item.category.name), 'pk': item.pk})

    def item_description(self, item):
        return item.description

    def item_pubdate(self, item):
        return item.upload_date

    def item_updateddate(self, item):
        return item.change_date

    def description(self, obj):
        return obj.description

    def items(self, obj):
        return models.Document.objects.filter(category=obj).order_by('-upload_date')[:10]


class DocumentDownload(View):
    def get(self, request, *args, **kwargs):
        # Get document or raise HTTP404
        doc = get_object_or_404(models.Document, pk=self.kwargs.get('pk'))
        # If document is an exam or marked as non-public, require login
        if doc.dtype == doc.DTypes.EXAM or doc.public is False:
            if not self.request.user.is_authenticated():
                return redirect('%s?next=%s' % (
                        reverse('auth_login'),
                        reverse('documents:document_list',
                                kwargs={'category': slugify(doc.category.name)})
                ))
        # Log download
        ip = helpers.get_client_ip(request)
        timerange = datetime.datetime.now() - datetime.timedelta(1)
        filters = {'document': doc, 'ip': ip, 'timestamp__gt': timerange}
        if not models.DocumentDownload.objects.filter(**filters).exists():
            models.DocumentDownload.objects.create(document=doc, ip=ip)
        # Serve file
        filename = unicodedata.normalize('NFKD', doc.original_filename) \
                              .encode('us-ascii', 'ignore')
        attachment = "inline" if filename.lower().endswith('.pdf') == True else "attachment"
        httpResponse = sendfile(request, doc.document.path)
        httpResponse['Content-Disposition'] = '%s; filename="%s"' % (attachment, filename)
        return httpResponse


class DocumentThumbnail(View):
    def generate_thumbnail(self, document_path, thumbnail_path):
        """Generate a thumbnail of the first page of a PDF by using imagemagick.
        :param document_path Path of the PDF to create thumbnail from
        :param thumbnail_path Path where to save the thumbnail
        :returns Tuple with wether operation was successful and message from stdout
        """
        params = ["-thumbnail", "400", document_path + "[0]", "-trim", thumbnail_path]
        proc = subprocess.check_output(["convert"] + params, stderr=subprocess.STDOUT)

    def get(self, request, *args, **kwargs):
        doc = get_object_or_404(models.Document, pk=self.kwargs.get('pk'))
        if not os.path.exists(doc.document.path):
            return HttpResponseBadRequest("Document has no file attached.")
        if not doc.document.path.lower().endswith(".pdf"):
            return HttpResponseBadRequest("File has to be a PDF to create a thumbnail")

        thumbnail_path = "{0}.png".format(doc.document.path)
        if not os.path.exists(thumbnail_path):
            try:
                self.generate_thumbnail(doc.document.path, thumbnail_path)
            except subprocess.CalledProcessError as e:
                logger.error('Thumbnail for {0} could not be created: {1}'
                             .format(doc.document.path, e))

        filename = unicodedata.normalize('NFKD', thumbnail_path).encode('us-ascii', 'ignore')
        return sendfile(request, thumbnail_path,
                        attachment=False, attachment_filename=filename)


class DocumentAddEditMixin(object):
    model = models.Document

    def get_context_data(self, **kwargs):
        context = super(DocumentAddEditMixin, self).get_context_data(**kwargs)
        context['exam_dtype_id'] = models.Document.DTypes.EXAM
        return context

    def get_success_url(self):
        """Redirect to documentcategory page."""
        messages.add_message(self.request, messages.SUCCESS,
            self.success_message)
        if hasattr(self, 'event_type') and self.event_type:
            messages.add_message(self.request, EVENT, self.event_type)
        return reverse('documents:document_list', args=[self.category])


class DocumentAdd(LoginRequiredMixin, DocumentAddEditMixin, DocumentcategoryMixin, CreateView):
    form_class = forms.DocumentAddForm
    success_message = 'Dokument wurde erfolgreich hinzugefügt.'
    event_type = 'document_add'

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


class DocumentEdit(LoginRequiredMixin, DocumentAddEditMixin, DocumentcategoryMixin, UpdateView):
    form_class = forms.DocumentEditForm
    success_message = 'Dokument wurde erfolgreich aktualisiert.'
    event_type = 'document_edit'

    def dispatch(self, request, *args, **kwargs):
        handler = super(DocumentEdit, self).dispatch(request, *args, **kwargs)
        # Only allow editing if current user is owner
        if self.object.uploader != request.user:
            return HttpResponseForbidden('Du darfst keine fremden Uploads editieren.')
        return handler


class DocumentDelete(LoginRequiredMixin, DocumentcategoryMixin, DeleteView):
    model = models.Document

    def get_success_url(self):
        """Redirect to documentcategory page."""
        messages.add_message(self.request, messages.SUCCESS,
            'Dokument wurde erfolgreich gelöscht.')
        messages.add_message(self.request, EVENT, 'document_delete')
        return reverse('documents:document_list', args=[self.category])


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
            return HttpResponseServerError('Required argument missing')
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
            return HttpResponseServerError('Validierungsfehler')
        rating.save()
        return HttpResponse('Bewertung wurde aktualisiert.')


class DocumentReport(DocumentcategoryMixin, SingleObjectMixin, FormView):
    model = models.Document
    form_class = forms.DocumentReportForm
    template_name = 'documents/document_report.html'
    context_object_name = 'document'

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()  # TODO can probably be removed in django 1.6
        return super(DocumentReport, self).dispatch(request, *args, **kwargs)

    def get_initial(self):
        if self.request.user.is_authenticated():
            return {
                'name': self.request.user.name(),
                'email': self.request.user.email,
            }

    def get_success_url(self):
        """Redirect to documentcategory page."""
        messages.add_message(self.request, messages.SUCCESS,
            'Vielen Dank, das Dokument wurde erfolgreich gemeldet.')
        messages.add_message(self.request, EVENT, 'document_report')
        return reverse('documents:document_list', args=[self.category])

    def form_valid(self, form):
        subject = '[studentenportal.ch] Neue Dokument-Meldung'
        sender = settings.DEFAULT_FROM_EMAIL
        receivers = [a[1] for a in settings.ADMINS]
        msg_tpl = 'Es gibt eine neue Meldung zum Dokument "{document.name}" ' + \
                  '(PK {document.pk}):\n\n' + \
                  'Melder: {name} ({email})\n' + \
                  'Grund: {reason}\n' + \
                  'Nachricht: {comment}\n\n' + \
                  'Link auf Dokument: https://studentenportal.ch{url}'
        admin_url = reverse('admin:documents_document_change', args=(self.object.pk,))
        msg = msg_tpl.format(document=self.object, url=admin_url, **form.cleaned_data)
        send_mail(subject, msg, sender, receivers, fail_silently=False)

        return super(DocumentReport, self).form_valid(form)


def document_rating(request, category, pk):
    """AJAX view that returns the document_rating_summary block. This is used
    to update the text after changing a rating via JavaScript."""
    if not request.is_ajax():
        return HttpResponseBadRequest('XMLHttpRequest expected.')
    if not request.user.is_authenticated():
        return HttpResponseForbidden('Login required')
    template = 'front/blocks/document_rating_summary.html'
    context = {'doc': get_object_or_404(models.Document, pk=pk, category__name=category)}
    return render(request, template, context, content_type='text/plain')
