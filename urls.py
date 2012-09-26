from registration.views import register
from dajaxice.core import dajaxice_autodiscover, dajaxice_config
from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
from django.contrib import admin
from apps.front import views
from apps.front.api.tools import api

admin.autodiscover()
dajaxice_autodiscover()

# Dynamic pages
urlpatterns = patterns('apps.front.views',
    url(r'^$', views.Home.as_view(), name='home'),
    url(r'^profil/$', views.Profile.as_view(), name='profile'),
    url(r'^events/$', views.EventList.as_view(), name='event_list'),
    url(r'^events/add/$', views.EventAdd.as_view(), name='event_add'),
    url(r'^events/(?P<pk>\d+)/$', views.Event.as_view(), name='event_detail'),
    url(r'^events/(?P<pk>\d+)/edit/$', views.EventEdit.as_view(), name='event_edit'),
    url(r'^events/(?P<pk>\d+)/delete/$', views.EventDelete.as_view(), name='event_delete'),
    url(r'^events/calendar.ics$', views.EventCalendar.as_view(), name='event_calendar'),
    url(r'^dozenten/$', views.LecturerList.as_view(), name='lecturer_list'),
    url(r'^dozenten/(?P<pk>\d+)/$', views.Lecturer.as_view(), name='lecturer_detail'),
    url(r'^dozenten/(?P<pk>\d+)/rate/$', views.LecturerRate.as_view(), name='lecturer_rate'),
    url(r'^zitate/$', views.QuoteList.as_view(), name='quote_list'),
    url(r'^zitate/add/$', views.QuoteAdd.as_view(), name='quote_add'),
    url(r'^zitate/(?P<pk>\d+)/add/$', views.QuoteAdd.as_view(), name='lecturer_quote_add'),
    url(r'^zitate/(?P<pk>\d+)/delete/$', views.QuoteDelete.as_view(), name='quote_delete'),
    url(r'^dokumente/$', views.DocumentcategoryList.as_view(), name='documentcategory_list'),
    url(r'^dokumente/add/$', views.DocumentcategoryAdd.as_view(), name='documentcategory_add'),
    url(r'^dokumente/(?P<category>[^\/]+)/$', views.DocumentList.as_view(), name='document_list'),
    url(r'^dokumente/(?P<category>[^\/]+)/(?P<pk>\d+)/$', views.DocumentDownload.as_view(), name='document_download'),
    url(r'^dokumente/(?P<category>[^\/]+)/add/$', views.DocumentAdd.as_view(), name='document_add'),
    url(r'^dokumente/(?P<category>[^\/]+)/(?P<pk>\d+)/edit/$', views.DocumentEdit.as_view(), name='document_edit'),
    url(r'^dokumente/(?P<category>[^\/]+)/(?P<pk>\d+)/delete/$', views.DocumentDelete.as_view(), name='document_delete'),
    url(r'^dokumente/(?P<category>[^\/]+)/(?P<pk>\d+)/rate/$', views.DocumentRate.as_view(), name='document_rate'),
    url(r'^dokumente/(?P<category>[^\/]+)/ajax_rating_block/(?P<pk>\d+)/$', views.document_rating, name='document_rating_ajax'),
    url(r'^users/(?P<pk>\d+)/(?P<username>[^\/]+)/$', views.User.as_view(), name='user'),
    url(r'^statistiken/$', views.Stats.as_view(), name='stats'),
)

# Static pages
urlpatterns += patterns('django.views.generic.simple',
    url(r'^tipps/$', 'direct_to_template', {'template': 'front/tips.html'}, name='tips'),
    url(r'^sitemap\.xml$', 'direct_to_template', {'template': 'front/sitemap.xml'}, name='sitemap'),
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
    url(r'^api/', include(api.urls)),
)


if settings.DEBUG:
    urlpatterns += patterns('django.views.static',
        url(r'static/(?P<path>.*)$', 'serve', {'document_root': settings.STATIC_ROOT}),
        url(r'media/(?P<path>.*)$', 'serve', {'document_root': settings.MEDIA_ROOT}),
    )
