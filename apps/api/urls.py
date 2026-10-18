from django.urls import include, re_path
from rest_framework.urlpatterns import format_suffix_patterns

from apps.api import views

app_name = "api"


v1_api = [
    re_path(r"^$", views.ApiRoot.as_view(), name="api_root"),
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
    re_path(r"^documents$", views.DocumentList.as_view(), name="document_list"),
    re_path(
        r"^documents/(?P<pk>-?\d+)$",
        views.DocumentDetail.as_view(),
        name="document_detail",
    ),
    re_path(
        r"^documents/(?P<pk>-?\d+)/rate$",
        views.DocumentRate.as_view(),
        name="document_rate",
    ),
    re_path(
        r"^documentcategories$",
        views.DocumentCategoryList.as_view(),
        name="documentcategory_list",
    ),
    re_path(
        r"^documentcategories/(?P<pk>-?\d+)$",
        views.DocumentCategoryDetail.as_view(),
        name="documentcategory_detail",
    ),
    re_path(r"^events$", views.EventList.as_view(), name="event_list"),
    re_path(
        r"^events/(?P<pk>-?\d+)$", views.EventDetail.as_view(), name="event_detail"
    ),
    re_path(r"^tipps$", views.TippList.as_view(), name="tipp_list"),
    re_path(r"^tipps/(?P<pk>-?\d+)$", views.TippDetail.as_view(), name="tipp_detail"),
    re_path(r"^tipps/(?P<pk>-?\d+)/vote$", views.TippVote.as_view(), name="tipp_vote"),
    re_path(
        r"^tipps/(?P<tpk>-?\d+)/comments$",
        views.TippCommentList.as_view(),
        name="tipp_comment_list",
    ),
    re_path(
        r"^tipps/(?P<tpk>-?\d+)/comments/(?P<pk>-?\d+)$",
        views.TippCommentDetail.as_view(),
        name="tipp_comment_detail",
    ),
]

urlpatterns = [
    re_path(r"^", include("rest_framework.urls")),
    re_path(r"^v1/", include(format_suffix_patterns(v1_api))),
]
