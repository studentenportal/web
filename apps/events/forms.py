# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from django import forms

from apps.events import models


class EventForm(forms.ModelForm):
    class Meta:
        model = models.Event
        exclude = ("author",)
