from django import forms

from apps.tipps import models


class TippForm(forms.ModelForm):
    class Meta:
        model = models.Tipp
        exclude = ("author", "date")


class TippCommentForm(forms.ModelForm):
    class Meta:
        model = models.TippComment
        fields = ("text",)
