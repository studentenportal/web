# coding=utf-8
from django import forms
from django.conf import settings
from django.contrib.auth import models as auth_models
from django.template.defaultfilters import filesizeformat
from registration.forms import RegistrationForm
from apps.front import models


class ProfileForm(forms.ModelForm):
    #username = forms.CharField(label=u'E-Mail', required=True)
    class Meta:
        model = auth_models.User
        fields = ('first_name', 'last_name', 'email')


class PasswordForm(forms.Form):
    password1 = forms.CharField(widget=forms.PasswordInput, label=u'Passwort')
    password2 = forms.CharField(widget=forms.PasswordInput, label=u'Passwort (Wiederholung)')


class EventForm(forms.ModelForm):
    class Meta:
        model = models.Event
        exclude = ('author',)


class QuoteForm(forms.ModelForm):
    def __init__(self, lecturer_id, *args, **kwargs):
        """This form takes a lecturer_id or None as the first argument.
        If a lecturer id is provided, it will be set as initial value
        for the dropdown."""
        super(QuoteForm, self).__init__(*args, **kwargs)
        if lecturer_id:
            self.fields['lecturer'].initial = lecturer_id

    class Meta:
        model = models.Quote
        exclude = ('author', 'date')


class HsrRegistrationForm(RegistrationForm):
        """Subclass of RegistrationForm which does not require
        an e-mail address.
        
        """
        def __init__(self, *args, **kwargs):
            super(HsrRegistrationForm, self).__init__(*args, **kwargs)
            del self.fields['email']  # Remove email field

        def clean_username(self):
            data = self.cleaned_data.get('username')
            if '@' in data:
                raise forms.ValidationError(u'Bitte nur vorderen Teil der Mailadresse ohne "@" eintragen.')
            return super(HsrRegistrationForm, self).clean_username()


class DocumentForm(forms.ModelForm):
    def clean_document(self):
        document = self.cleaned_data['document']
        if document.size > settings.MAX_UPLOAD_SIZE:
            raise forms.ValidationError(u'Bitte Dateigrösse unter %s halten. Aktuelle Dateigrösse ist %s' %
                    (filesizeformat(settings.MAX_UPLOAD_SIZE), filesizeformat(document._size)))
        return document

    class Meta:
        model = models.Document
        exclude = ('category', 'uploader')
