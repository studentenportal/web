# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _


class CaseInsensitiveSlugField(models.SlugField):
    """
    A SlugField that uses the PostgreSQL CITEXT type for
    case insensitive comparison.
    """
    description = _('A SlugField that uses the PostgreSQL CITEXT type for \
                     case insensitive comparison.')

    def db_type(self, connection):
        return 'CITEXT'
