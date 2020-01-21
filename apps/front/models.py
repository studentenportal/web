# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.safestring import mark_safe


def strip_mail_part(username):
    """
    Users might try to login with their email. To support that
    we can simply strip the mail part from the username
    """
    if '@' in username:
        return username.split('@')[0]
    return username


class CustomUserManager(BaseUserManager):

    """
    By default, django.contrib.auth does case _sensitive_ username authentication, which isn't what is
    generally expected. By defining a custom user manager, we can compare user
    names case insensitively and strip off the email part.

    Sources:

    https://djangosnippets.org/snippets/1368/
    https://code.djangoproject.com/ticket/2273#comment:12
    """

    def get_by_natural_key(self, username):
        username = strip_mail_part(username)
        return self.get(username__iexact=username)


class User(AbstractUser):
    """The user model."""
    twitter = models.CharField('Twitter Benutzername', max_length=24, blank=True)
    flattr = models.CharField('Flattr Benutzername', max_length=128, blank=True,
            help_text=mark_safe('Falls angegeben, wird bei deinen Zusammenfassungen jeweils ein '
            '<a href="https://flattr.com/">Flattr</a> Button angezeigt.'))

    users = CustomUserManager()

    def name(self):
        """Return either full user first and last name or the username, if no
        further data is found."""
        if self.first_name or self.last_name:
            return ' '.join(part for part in [self.first_name, self.last_name] if part)
        return self.username
