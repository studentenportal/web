# -*- coding: utf-8 -*-
"""Helper functions."""
from __future__ import print_function, division, absolute_import, unicode_literals


def get_client_ip(request):
    """Returns the remote IP address of a request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
