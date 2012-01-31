from django import forms
from apps.front import models


class ProfileForm(forms.Form):
    username = forms.CharField(label=u'E-Mail', required=True)


class PasswordForm(forms.Form):
    password1 = forms.CharField(widget=forms.PasswordInput, label=u'Passwort')
    password2 = forms.CharField(widget=forms.PasswordInput, label=u'Passwort (Wiederholung)')


class EventForm(forms.ModelForm):
    class Meta:
        model = models.Event
        exclude = ('author',)
