# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from django import forms

from apps.events import models


class EventForm(forms.ModelForm):
    class Meta:
        model = models.Event
        exclude = ("author",)
