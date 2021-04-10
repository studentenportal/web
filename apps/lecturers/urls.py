from django.contrib import admin
from django.urls import re_path

from apps.lecturers import views


admin.autodiscover()

app_name = "lecturers"

# Dynamic pages
urlpatterns = [
    re_path(r"^dozenten/$", views.LecturerList.as_view(), name="lecturer_list"),
    re_path(
        r"^dozenten/(?P<pk>-?\d+)/$", views.Lecturer.as_view(), name="lecturer_detail"
    ),
    re_path(r"^dozenten/add/$", views.LecturerAdd.as_view(), name="lecturer_add"),
    re_path(r"^zitate/$", views.QuoteList.as_view(), name="quote_list"),
    re_path(r"^zitate/add/$", views.QuoteAdd.as_view(), name="quote_add"),
    re_path(
        r"^zitate/(?P<pk>-?\d+)/add/$",
        views.QuoteAdd.as_view(),
        name="lecturer_quote_add",
    ),
    re_path(
        r"^zitate/(?P<pk>-?\d+)/delete/$",
        views.QuoteDelete.as_view(),
        name="quote_delete",
    ),
]
