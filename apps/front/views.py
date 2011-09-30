from django.contrib.auth.decorators import login_required
from apps.front.decorators import render_to
from apps.front import forms


@render_to('home.html')
def home(request):
    return {}


@login_required
@render_to('profil.html')
def profil(request):
    profile_form = forms.ProfileForm(initial={'username': 'danilo'})
    return {
        'form': profile_form,
    }


def termine(request):
    pass


@render_to('dozenten.html')
def dozenten(request):
    return {}
