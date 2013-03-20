# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from django.contrib.auth import models as auth_models

from rest_framework import generics
from rest_framework import permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

from apps.front import models
from . import permissions as custom_permissions
from . import serializers


@api_view(('GET',))
def api_root(request, format=None):
    return Response({
        'users': reverse('user_list', request=request, format=format),
        'lecturers': reverse('lecturer_list', request=request, format=format),
        'quotes': reverse('quote_list', request=request, format=format),
    })


class UserList(generics.ListAPIView):
    model = auth_models.User
    serializer_class = serializers.UserSerializer


class UserDetail(generics.RetrieveUpdateAPIView):
    model = auth_models.User
    serializer_class = serializers.UserSerializer


class LecturerList(generics.ListAPIView):
    queryset = models.Lecturer.real_objects.all()
    serializer_class = serializers.LecturerSerializer


class LecturerDetail(generics.RetrieveAPIView):
    queryset = models.Lecturer.real_objects.all()
    serializer_class = serializers.LecturerSerializer


class QuoteList(generics.ListCreateAPIView):
    model = models.Quote
    serializer_class = serializers.QuoteSerializer

    def pre_save(self, obj):
        obj.author = self.request.user


class QuoteDetail(generics.RetrieveUpdateAPIView):
    model = models.Quote
    serializer_class = serializers.QuoteSerializer
    owner_field = 'author'
    permission_classes = (
        custom_permissions.IsOwnerOrReadOnly,
    )

    def pre_save(self, obj):
        obj.author = self.request.user
