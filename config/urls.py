from registration.views import register
from dajaxice.core import dajaxice_autodiscover, dajaxice_config
from django.conf.urls import patterns, include, url
from django.conf import settings
from django.views.generic import TemplateView
from django.contrib import admin
from apps.front import views
from apps.api import urls as api_urls
from apps.events import urls as events_urls
from apps.lecturers import urls as lecturers_urls

admin.autodiscover()
dajaxice_autodiscover()

# Dynamic pages
urlpatterns = patterns('apps.front.views',
    url(r'^$', views.Home.as_view(), name='home'),
    url(r'^profil/$', views.Profile.as_view(), name='profile'),
    url(r'^dokumente/$', views.DocumentcategoryList.as_view(), name='documentcategory_list'),
    url(r'^dokumente/add/$', views.DocumentcategoryAdd.as_view(), name='documentcategory_add'),
    url(r'^dokumente/(?P<category>[^\/]+)/$', views.DocumentList.as_view(), name='document_list'),
    url(r'^dokumente/(?P<category>[^\/]+)/(?P<pk>-?\d+)/$', views.DocumentDownload.as_view(), name='document_download'),
    url(r'^dokumente/(?P<category>[^\/]+)/add/$', views.DocumentAdd.as_view(), name='document_add'),
    url(r'^dokumente/(?P<category>[^\/]+)/(?P<pk>-?\d+)/edit/$', views.DocumentEdit.as_view(), name='document_edit'),
    url(r'^dokumente/(?P<category>[^\/]+)/(?P<pk>-?\d+)/delete/$', views.DocumentDelete.as_view(), name='document_delete'),
    url(r'^dokumente/(?P<category>[^\/]+)/(?P<pk>-?\d+)/rate/$', views.DocumentRate.as_view(), name='document_rate'),
    url(r'^dokumente/(?P<category>[^\/]+)/(?P<pk>-?\d+)/report/$', views.DocumentReport.as_view(), name='document_report'),
    url(r'^dokumente/(?P<category>[^\/]+)/ajax_rating_block/(?P<pk>-?\d+)/$', views.document_rating, name='document_rating_ajax'),
    url(r'^users/(?P<pk>-?\d+)/(?P<username>[^\/]+)/$', views.User.as_view(), name='user'),
    url(r'^statistiken/$', views.Stats.as_view(), name='stats'),
)

# Static pages
urlpatterns += patterns('',
    url(r'^tipps/$', TemplateView.as_view(template_name='front/tips.html'), name='tips'),
    url(r'^sitemap\.xml$', TemplateView.as_view(template_name='front/sitemap.xml'), name='sitemap'),
)

# Auth pages
urlpatterns += patterns('',
    url(r'^accounts/register/$', register, {'backend': 'apps.front.registration_backends.HsrEmailBackend'}, name='register'),
    url(r'^accounts/', include('registration.backends.default.urls')),
)

# Admin pages
urlpatterns += patterns('',
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)

# AJAX
urlpatterns += patterns('',
    url(dajaxice_config.dajaxice_url, include('dajaxice.urls')),    
)

# API
urlpatterns += patterns('',
    url(r'^api/', include(api_urls, namespace='api')),
    url(r'^oauth2/', include('provider.oauth2.urls', namespace='oauth2')),
)

# Events
urlpatterns += patterns('', url(r'^events/', include(events_urls, namespace='events')))

# Lecturers
urlpatterns += patterns('', url(r'^$', include(lecturers_urls, namespace='lecturers')))


if settings.DEBUG:
    urlpatterns += patterns('django.views.static',
        url(r'static/(?P<path>.*)$', 'serve', {'document_root': settings.STATIC_ROOT}),
        url(r'media/(?P<path>.*)$', 'serve', {'document_root': settings.MEDIA_ROOT}),
    )
