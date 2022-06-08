from django.contrib import admin
from django.urls import re_path

from . import views

admin.autodiscover()

app_name = "documents"

# Dynamic pages
urlpatterns = [
    re_path(r"^$", views.DocumentcategoryList.as_view(), name="documentcategory_list"),
    re_path(
        r"^add/$", views.DocumentcategoryAdd.as_view(), name="documentcategory_add"
    ),
    re_path(
        r"^(?P<category>[^\/]+)/$", views.DocumentList.as_view(), name="document_list"
    ),
    re_path(r"^(?P<category>[^\/]+)/rss$", views.DocumentFeed(), name="document_feed"),
    re_path(
        r"^(?P<category>[^\/]+)/(?P<pk>-?\d+)/$",
        views.DocumentDownload.as_view(),
        name="document_download",
    ),
    re_path(
        r"^(?P<category>[^\/]+)/thumbnail/(?P<pk>-?\d+)/$",
        views.DocumentThumbnail.as_view(),
        name="document_thumbnail",
    ),
    re_path(
        r"^(?P<category>[^\/]+)/add/$", views.DocumentAdd.as_view(), name="document_add"
    ),
    re_path(
        r"^(?P<category>[^\/]+)/(?P<pk>-?\d+)/edit/$",
        views.DocumentEdit.as_view(),
        name="document_edit",
    ),
    re_path(
        r"^(?P<category>[^\/]+)/(?P<pk>-?\d+)/delete/$",
        views.DocumentDelete.as_view(),
        name="document_delete",
    ),
    re_path(
        r"^(?P<category>[^\/]+)/(?P<pk>-?\d+)/rate/$",
        views.DocumentRate.as_view(),
        name="document_rate",
    ),
    re_path(
        r"^(?P<category>[^\/]+)/ajax_rating_block/(?P<pk>-?\d+)/$",
        views.document_rating,
        name="document_rating_ajax",
    ),
]
