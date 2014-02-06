# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from django.contrib.auth import get_user_model

from rest_framework import generics, permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

from apps.lecturers import models
from . import permissions as custom_permissions
from . import serializers


@api_view(('GET',))
def api_root(request, format=None):
    return Response({
        'users': reverse('api:user_list', request=request, format=format),
        'lecturers': reverse('api:lecturer_list', request=request, format=format),
        'quotes': reverse('api:quote_list', request=request, format=format),
    })


# GET
class UserList(generics.ListAPIView):
    model = get_user_model()
    serializer_class = serializers.UserSerializer


# GET / PUT / PATCH
class UserDetail(generics.RetrieveUpdateAPIView):
    model = get_user_model()
    serializer_class = serializers.UserSerializer
    owner_username_field = 'username'
    permission_classes = (
        permissions.IsAuthenticated,
        custom_permissions.IsOwnerOrReadOnly,
    )


# GET
class LecturerList(generics.ListAPIView):
    queryset = models.Lecturer.real_objects.all()
    serializer_class = serializers.LecturerSerializer


# GET
class LecturerDetail(generics.RetrieveAPIView):
    queryset = models.Lecturer.real_objects.all()
    serializer_class = serializers.LecturerSerializer


# GET / POST
class QuoteList(generics.ListCreateAPIView):
    model = models.Quote
    serializer_class = serializers.QuoteSerializer

    def pre_save(self, obj):
        obj.author = self.request.user


# GET / PUT / PATCH
class QuoteDetail(generics.RetrieveUpdateAPIView):
    model = models.Quote
    serializer_class = serializers.QuoteSerializer
    owner_obj_field = 'author'
    permission_classes = (
        permissions.IsAuthenticated,
        custom_permissions.IsOwnerOrReadOnly,
    )
