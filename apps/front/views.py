from django.contrib.auth.decorators import login_required
from apps.front.decorators import render_to
from apps.front import forms
from apps.front import models


@render_to('home.html')
def home(request):
    return {}


@login_required
@render_to('profile.html')
def profile(request):
    profile_form = forms.ProfileForm(initial={'username': 'danilo'})
    return {
        'form': profile_form,
    }


@render_to('calendar.html')
def calendar(request):
    pass


@render_to('lecturers.html')
def lecturers(request):
    lecturers = models.Lecturer.objects.all()

    return {
        'lecturers': (lecturers[::2], lecturers[1::2]),
    }


@render_to('documents.html')
def documents(request):
    return {}
