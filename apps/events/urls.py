from django.contrib import admin
from django.urls import re_path

from . import views

admin.autodiscover()

app_name = "events"

# Dynamic pages
urlpatterns = [
    re_path(r"^$", views.EventList.as_view(), name="event_list"),
    re_path(r"^add/$", views.EventAdd.as_view(), name="event_add"),
    re_path(r"^(?P<pk>-?\d+)/$", views.Event.as_view(), name="event_detail"),
    re_path(r"^(?P<pk>-?\d+)/edit/$", views.EventEdit.as_view(), name="event_edit"),
    re_path(
        r"^(?P<pk>-?\d+)/delete/$", views.EventDelete.as_view(), name="event_delete"
    ),
    re_path(r"^calendar.ics$", views.EventCalendar.as_view(), name="event_calendar"),
]
