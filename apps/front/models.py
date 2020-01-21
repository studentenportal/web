# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.safestring import mark_safe


class User(AbstractUser):
    """The user model."""
    twitter = models.CharField('Twitter Benutzername', max_length=24, blank=True)
    flattr = models.CharField('Flattr Benutzername', max_length=128, blank=True,
            help_text=mark_safe('Falls angegeben, wird bei deinen Zusammenfassungen jeweils ein '
            '<a href="https://flattr.com/">Flattr</a> Button angezeigt.'))

    def name(self):
        """Return either full user first and last name or the username, if no
        further data is found."""
        if self.first_name or self.last_name:
            return ' '.join(part for part in [self.first_name, self.last_name] if part)
        return self.username
