# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from django.contrib import admin

from apps.events import models

admin.site.register(models.Event)
