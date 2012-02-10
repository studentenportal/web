from django import forms
from django.contrib.auth import models as auth_models
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
