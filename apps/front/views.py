# coding=utf-8
import datetime
from django.contrib.auth.decorators import login_required
from django.views import generic
from django.views.generic.list import ListView
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


class Events(ListView):
    queryset = models.Event.objects.filter(start_date__gte=datetime.date.today()).order_by('start_date', 'start_time')
    context_object_name = 'events'


@render_to('lecturers.html')
def lecturers(request):
    lecturers = models.Lecturer.objects.all()
    return {
        'lecturers': (lecturers[::2], lecturers[1::2]),
    }


class DocumentCategories(generic.list.ListView):
    template_name = 'document_categories.html'
    model = models.DocumentCategory


@render_to('document_category.html')
def document_category(request, category):
    return {
        'object_list': models.DocumentCategory.objects.get(name__iexact=category).Document.all(),
    }
