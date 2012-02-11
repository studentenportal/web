from django import forms
from django.contrib.auth import models as auth_models
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


class HsrRegistrationForm(RegistrationForm):
        """Subclass of RegistrationForm which does not require
        an e-mail address.
        
        """
        def __init__(self, *args, **kwargs):
            super(HsrRegistrationForm, self).__init__(*args, **kwargs)
            del self.fields['email']  # Remove email field
