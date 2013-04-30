# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Only allow owners of an object to edit it."""

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the snippet
        return getattr(obj, view.owner_field) == request.user
