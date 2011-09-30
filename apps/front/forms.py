from django import forms

class ProfileForm(forms.Form):
    username = forms.CharField(label=u'E-Mail', required=True)

class PasswordForm(forms.Form):
    password1 = forms.CharField(widget=forms.PasswordInput, label=u'Passwort')
    password2 = forms.CharField(widget=forms.PasswordInput, label=u'Passwort (Wiederholung)')
