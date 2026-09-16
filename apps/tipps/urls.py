from django.contrib import admin
from django.urls import re_path

from . import views

admin.autodiscover()

app_name = "tipps"

# Dynamic pages
urlpatterns = [
    re_path(r"^$", views.TippList.as_view(), name="tipp_list"),
    re_path(r"^add/$", views.TippAdd.as_view(), name="tipp_add"),
    re_path(
        r"^(?P<pk>-?\d+)/edit/$",
        views.TippEdit.as_view(),
        name="tipp_edit",
    ),
    re_path(
        r"^(?P<pk>-?\d+)/delete/$",
        views.TippDelete.as_view(),
        name="tipp_delete",
    ),
    re_path(r"^(?P<pk>-?\d+)/vote$", views.TippVote.as_view(), name="tipp_vote"),
    re_path(
        r"^(?P<pk>-?\d+)/comment/add/$",
        views.TippCommentAdd.as_view(),
        name="tipp_comment_add",
    ),
    re_path(
        r"^comment/(?P<pk>-?\d+)/edit/$",
        views.TippCommentEdit.as_view(),
        name="tipp_comment_edit",
    ),
    re_path(
        r"^comment/(?P<pk>-?\d+)/delete/$",
        views.TippCommentDelete.as_view(),
        name="tipp_comment_delete",
    ),
]
