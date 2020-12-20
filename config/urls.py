from django.conf import settings
from django.contrib import admin
from django.views.generic import TemplateView
from django.views.static import serve
from django.urls import include, re_path

from apps.api import urls as api_urls
from apps.documents import urls as document_urls
from apps.events import urls as event_urls
from apps.front import views
from apps.lecturers import urls as lecturer_urls

admin.autodiscover()

urlpatterns = [
    # Dynamic pages
    re_path(r"^$", views.Home.as_view(), name="home"),
    re_path(r"^profil/$", views.Profile.as_view(), name="profile"),
    re_path(
        r"^users/(?P<pk>-?\d+)/(?P<username>[^\/]+)/$",
        views.User.as_view(),
        name="user",
    ),
    re_path(r"^statistiken/$", views.Stats.as_view(), name="stats"),
    # Own apps
    re_path(r"^events/", include(event_urls)),
    re_path(r"^dokumente/", include(document_urls)),
    re_path(r"", include(lecturer_urls)),
    # Auth pages
    re_path(r"^accounts/", include("registration.backends.default.urls")),
    # Admin pages
    re_path(r"^admin/doc/", include("django.contrib.admindocs.urls")),
    re_path(r"^admin/", admin.site.urls),
    # API
    re_path(r"^api/", include(api_urls)),
    # Static pages
    re_path(
        r"^sitemap\.xml$",
        TemplateView.as_view(template_name="front/sitemap.xml"),
        name="sitemap",
    ),
]

if settings.DEBUG:
    urlpatterns += [
        re_path(
            r"static/(?P<path>.*)$", serve, {"document_root": settings.STATIC_ROOT}
        ),
        re_path(r"media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
    ]

if settings.DEBUG_TOOLBAR:
    import debug_toolbar

    urlpatterns += [
        re_path(r"^__debug__/", include(debug_toolbar.urls)),
    ]
