from django import forms

from apps.lecturers import models


class LecturerForm(forms.ModelForm):
    class Meta:
        model = models.Lecturer
        fields = (
            "title",
            "last_name",
            "first_name",
            "abbreviation",
            "department",
            "function",
            "main_area",
            "subjects",
            "email",
            "office",
            "picture",
        )


class QuoteForm(forms.ModelForm):
    def __init__(self, lecturer_id, *args, **kwargs):
        """This form takes a lecturer_id or None as the first argument.
        If a lecturer id is provided, it will be set as initial value
        for the dropdown."""
        super().__init__(*args, **kwargs)
        if lecturer_id:
            self.fields["lecturer"].initial = lecturer_id

    class Meta:
        model = models.Quote
        exclude = ("author", "date")
