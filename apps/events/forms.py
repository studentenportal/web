from django import forms

from apps.events import models


class EventForm(forms.ModelForm):
    class Meta:
        model = models.Event
        exclude = ("author",)
