# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import sys

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


class LoginRequiredMixin(object):
    """Ensures that user must be authenticated in order to access view."""
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(*args, **kwargs)


class CommandOutputMixin(object):
    """Mixin to provide printO and printE methods."""

    def printO(self, msg):
        """Print to stdout. This expects unicode strings!"""
        encoding = self.stdout.encoding or sys.getdefaultencoding()
        self.stdout.write(msg.encode(encoding, 'replace'))

    def printE(self, msg):
        """Print to stderr. This expects unicode strings!"""
        encoding = self.stderr.encoding or sys.getdefaultencoding()
        self.stderr.write(msg.encode(encoding, 'replace'))
