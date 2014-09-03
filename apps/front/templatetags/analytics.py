# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from django import template
from django.conf import settings

register = template.Library()


class ShowGoogleAnalyticsJS(template.Node):
    def render(self, context):
        code = getattr(settings, 'GOOGLE_ANALYTICS_CODE', False)
        if not code:
            return '<!-- Goggle Analytics not included because you haven\'t set the ' + \
                   'settings.GOOGLE_ANALYTICS_CODE variable! -->'

        if 'user' in context and context['user'] and context['user'].is_staff:
            return '<!-- Goggle Analytics not included because you are a staff user! -->'

        if settings.DEBUG:
            return '<!-- Goggle Analytics not included because you are in debug mode! -->'

        return """
        <script>
            (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
            (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
            m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
            })(window,document,'script','//www.google-analytics.com/analytics.js','ga');
            ga('create', '%s', 'auto');
            ga('send', 'pageview');
        </script>
        """ % code


def googleanalyticsjs(parser, token):
    return ShowGoogleAnalyticsJS()

show_common_data = register.tag(googleanalyticsjs)
