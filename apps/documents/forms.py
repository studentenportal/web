# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from datetime import datetime

from django import forms
from django.conf import settings
from django.template.defaultfilters import filesizeformat

from . import models


class DocumentCategoryForm(forms.ModelForm):
    class Meta:
        model = models.DocumentCategory
        fields = ('name', 'description')


class DocumentEditForm(forms.ModelForm):

    def clean_document(self):
        document = self.cleaned_data['document']
        if hasattr(document, '_size'):
            if document.size > settings.MAX_UPLOAD_SIZE:
                error_msg = 'Bitte Dateigrösse unter %s halten. Aktuelle Dateigrösse ist %s'
                sizes = filesizeformat(settings.MAX_UPLOAD_SIZE), filesizeformat(document._size)
                raise forms.ValidationError(error_msg % sizes)
        return document

    def clean(self):
        cleaned_data = super(DocumentEditForm, self).clean()
        public = cleaned_data.get('public')
        dtype = cleaned_data.get('dtype')

        # Verify that exams are non-public
        if dtype == models.Document.DTypes.EXAM and public is True:
            self._errors['public'] = self.error_class(['Prüfungen dürfen nicht öffentlich sein.'])
            del cleaned_data['public']

        return cleaned_data

    def save(self, *args, **kwargs):
        """Override save method, set change_date to now only if pdf is actually updated."""
        if 'document' in self.changed_data:
            self.instance.change_date = datetime.now()
        return super(DocumentEditForm, self).save(*args, **kwargs)

    class Meta:
        model = models.Document
        fields = ('name', 'description', 'url', 'category', 'dtype', 'document',
                  'license', 'public', 'flattr_disabled')
        widgets = {
            'description': forms.Textarea(),
        }


class DocumentAddForm(DocumentEditForm):
    class Meta(DocumentEditForm.Meta):
        fields = ('name', 'description', 'url', 'dtype', 'document', 'license',
                  'public', 'flattr_disabled')


class DocumentReportForm(forms.Form):
    name = forms.CharField()
    email = forms.EmailField()
    reason = forms.ChoiceField(choices=(
        ('other', 'Sonstiges'),
        ('wrong_category', 'Falsche Kategorie'),
        ('outdated', 'Veraltet'),
        ('bad_content', 'Schlechter Inhalt'),
    ), label='Begründung')
    comment = forms.CharField(label='Kommentar', widget=forms.Textarea())
