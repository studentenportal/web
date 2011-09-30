from django.conf.urls.defaults import patterns, include, url
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

# Dynamic pages
urlpatterns = patterns('apps.front.views',
    url(r'^$', 'home', name='home'),
    url(r'^profil/$', 'profil', name='profil'),
    url(r'^termine/$', 'termine', name='termine'),
    url(r'^dozenten/$', 'dozenten', name='dozenten'),
)

# Static pages
urlpatterns += patterns('django.views.generic.simple',
    url(r'^tipps/$', 'direct_to_template', {'template': 'tipps.html'}, name='tipps'),
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
    )
