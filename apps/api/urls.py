from django.urls import include, re_path
from rest_framework.urlpatterns import format_suffix_patterns

from apps.api import views

app_name = "api"


v1_api = [
    re_path(r"^$", views.api_root, name="api_root"),
    re_path(r"^users$", views.UserList.as_view(), name="user_list"),
    re_path(r"^users/(?P<pk>-?\d+)$", views.UserDetail.as_view(), name="user_detail"),
    re_path(r"^lecturers$", views.LecturerList.as_view(), name="lecturer_list"),
    re_path(
        r"^lecturers/(?P<pk>-?\d+)$",
        views.LecturerDetail.as_view(),
        name="lecturer_detail",
    ),
    re_path(
        r"^lecturers/(?P<pk>-?\d+)/rate$",
        views.LecturerRate.as_view(),
        name="lecturer_rate",
    ),
    re_path(r"^quotes$", views.QuoteList.as_view(), name="quote_list"),
    re_path(
        r"^quotes/(?P<pk>-?\d+)$", views.QuoteDetail.as_view(), name="quote_detail"
    ),
    re_path(
        r"^quotes/(?P<pk>-?\d+)/vote$", views.QuoteVote.as_view(), name="quote_vote"
    ),
]

urlpatterns = [
    re_path(r"^", include("rest_framework.urls")),
    re_path(r"^v1/", include(format_suffix_patterns(v1_api))),
]
