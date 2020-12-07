from django.conf.urls import url
from django.contrib import admin
from apps.lecturers import views

admin.autodiscover()

app_name = "lecturers"

# Dynamic pages
urlpatterns = [
    url(r"^dozenten/$", views.LecturerList.as_view(), name="lecturer_list"),
    url(r"^dozenten/(?P<pk>-?\d+)/$", views.Lecturer.as_view(), name="lecturer_detail"),
    url(r"^zitate/$", views.QuoteList.as_view(), name="quote_list"),
    url(r"^zitate/add/$", views.QuoteAdd.as_view(), name="quote_add"),
    url(
        r"^zitate/(?P<pk>-?\d+)/add/$",
        views.QuoteAdd.as_view(),
        name="lecturer_quote_add",
    ),
    url(
        r"^zitate/(?P<pk>-?\d+)/delete/$",
        views.QuoteDelete.as_view(),
        name="quote_delete",
    ),
]
