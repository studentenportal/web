from django.conf.urls.defaults import patterns, include, url
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from apps.front import views


# Dynamic pages
urlpatterns = patterns('apps.front.views',
    url(r'^$', 'home', name='home'),
    url(r'^profil/$', 'profile', name='profile'),
    url(r'^events/$', views.EventList.as_view(), name='event_list'),
    url(r'^events/add/$', views.EventAdd.as_view(), name='event_add'),
    url(r'^events/(?P<pk>\d+)/$', views.Event.as_view(), name='event_detail'),
    url(r'^events/(?P<pk>\d+)/edit/$', views.EventEdit.as_view(), name='event_edit'),
    url(r'^events/(?P<pk>\d+)/delete/$', views.EventDelete.as_view(), name='event_delete'),
    url(r'^dozenten/$', 'lecturers', name='lecturers'),
    url(r'^zusammenfassungen/$', views.DocumentCategories.as_view(), name='document_categories'),
    url(r'^zusammenfassungen/(?P<category>.*)/$', 'document_category', name='document_category'),
    url(r'^users/(?P<pk>\d+)-(?P<username>[^\/]+)/$', 'home', name='user'),
)

# Static pages
urlpatterns += patterns('django.views.generic.simple',
    url(r'^tipps/$', 'direct_to_template', {'template': 'tips.html'}, name='tips'),
)

# Auth pages
urlpatterns += patterns('django.contrib.auth.views',
    url(r'^login/$', 'login', {'template_name': 'login.html'}, name='login'),
    url(r'^logout/$', 'logout', {'template_name': 'logout.html'}, name='logout'),
)

# Admin pages
urlpatterns += patterns('',
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)


if settings.DEBUG:
    urlpatterns += patterns('django.views.static',
        url(r'static/(?P<path>.*)$', 'serve', {'document_root': settings.STATIC_ROOT}),
        url(r'media/(?P<path>.*)$', 'serve', {'document_root': settings.MEDIA_ROOT}),
    )
