# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from django import forms
from django.contrib.auth import get_user_model

from registration.forms import RegistrationForm


class ProfileForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ('email', 'first_name', 'last_name', 'twitter', 'flattr')


class PasswordForm(forms.Form):
    password1 = forms.CharField(widget=forms.PasswordInput, label='Passwort')
    password2 = forms.CharField(widget=forms.PasswordInput, label='Passwort (Wiederholung)')


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
                error_msg = 'Bitte nur vorderen Teil der Mailadresse ohne "@" eintragen.'
                raise forms.ValidationError(error_msg)
            return super(HsrRegistrationForm, self).clean_username()
