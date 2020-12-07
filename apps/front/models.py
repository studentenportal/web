# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.utils.safestring import mark_safe


def strip_mail_part(username):
    """
    Users might try to login with their email. To support that
    we can simply strip the mail part from the username
    """
    if "@" in username:
        return username.split("@")[0]
    return username


class CustomUserManager(UserManager):

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

    users = CustomUserManager()

    def name(self):
        """Return either full user first and last name or the username, if no
        further data is found."""
        if self.first_name or self.last_name:
            return " ".join(part for part in [self.first_name, self.last_name] if part)
        return self.username
