from django.conf.urls import include, url
from django.conf import settings
from django.views.generic import TemplateView
from django.views.static import serve
from django.contrib import admin

from apps.front import views
from apps.api import urls as api_urls
from apps.events import urls as event_urls
from apps.documents import urls as document_urls
from apps.lecturers import urls as lecturer_urls
from apps.tweets import urls as tweet_urls

admin.autodiscover()

urlpatterns = [
    # Dynamic pages
    url(r'^$', views.Home.as_view(), name='home'),
    url(r'^profil/$', views.Profile.as_view(), name='profile'),
    url(r'^users/(?P<pk>-?\d+)/(?P<username>[^\/]+)/$', views.User.as_view(), name='user'),
    url(r'^statistiken/$', views.Stats.as_view(), name='stats'),

    # Own apps
    url(r'^events/', include(event_urls, namespace='events')),
    url(r'^dokumente/', include(document_urls, namespace='documents')),
    url(r'tweets/', include(tweet_urls, namespace='tweets')),
    url(r'', include(lecturer_urls, namespace='lecturers')),

    # Auth pages
    url(r'^accounts/', include('registration.backends.default.urls')),

    # Admin pages
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),

    # API
    url(r'^api/', include(api_urls, namespace='api')),

    # Static pages
    url(r'^sitemap\.xml$', TemplateView.as_view(template_name='front/sitemap.xml'), name='sitemap'),
]

if settings.DEBUG:
    urlpatterns += [
        url(r'static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
        url(r'media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    ]

if settings.DEBUG_TOOLBAR:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
