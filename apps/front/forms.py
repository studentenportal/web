# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import re

from django import forms
from django.contrib.auth import get_user_model

from registration.forms import RegistrationForm


USERNAME_REGEXES = {
    "hsr.ch": re.compile(r"^[a-zA-Z0-9-_]+$"),
    "ost.ch": re.compile(r"^[a-zA-Z0-9-_.]+$"),
}


class ProfileForm(forms.ModelForm):
    # Note: Don't allow users to change their own e-mail!
    class Meta:
        model = get_user_model()
        fields = ("first_name", "last_name")


class PasswordForm(forms.Form):
    password1 = forms.CharField(widget=forms.PasswordInput, label="Passwort")
    password2 = forms.CharField(
        widget=forms.PasswordInput, label="Passwort (Wiederholung)"
    )


class HsrRegistrationForm(RegistrationForm):
    """
    Subclass of RegistrationForm which derives the username from the e-mail.
    """

    # Override username field, make it non-required.
    # It will be filled in by the `clean` method.
    username = forms.CharField(label="Username", required=False)

    def clean_email(self):
        email = self.cleaned_data["email"]

        # Only allow HSR e-mails
        email_domain = email.split("@")[1]
        if email_domain not in USERNAME_REGEXES:
            raise forms.ValidationError(
                "Registrierung ist Studierenden mit einer @ost.ch oder @hsr.ch-Mailadresse vorbehalten."
            )

        User = get_user_model()

        # Ensure that user with this email does not exist yet
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Benutzer mit dieser E-Mail existiert bereits.")

        # Extract username from e-mail
        email_user = email.split("@")[0]
        username_re = USERNAME_REGEXES[email_domain]

        # Ensure that the username part is valid
        if not username_re.match(email_user):
            msg = "Ungültige E-Mail, Benutzername darf nur a-z, A-Z, 0-9, - und _ enthalten."
            if "." in email_user and email_domain == "hsr.ch":
                msg += " Nutze bitte mmuster@hsr.ch statt melanie.muster@hsr.ch."

            raise forms.ValidationError(msg)

        if email_domain == "ost.ch" and "." not in email_user:
            msg = "Ungültige E-Mail, Benutzername sollte . enthalten."
            raise forms.ValidationError(msg)

        # Ensure that user with this username does not exist yet
        # (We can't do this in the `clean_username` method since the `username`
        # field will only be written in the `clean` method.)
        if User.objects.filter(username__iexact=email_user).exists():
            raise forms.ValidationError(
                'Benutzer "{}" existiert bereits.'.format(email_user)
            )

        return email

    def clean(self):
        cleaned = super(HsrRegistrationForm, self).clean()

        # Determine the username based on the e-mail
        email = cleaned.get("email")
        if email is None:
            # Note: If the e-mail is none, that means that the e-mail validation failed.
            # In that case there will already be an error shown.
            assert (
                self.errors is not None and len(self.errors) > 0
            ), "Email is not set even though no errors were reported by validation"
        else:
            username = email.split("@")[0]
            cleaned["username"] = username
            self.instance.username = username

        return cleaned

    class Meta:
        model = get_user_model()
        fields = ("email",)
