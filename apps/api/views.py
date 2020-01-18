# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.http import HttpResponseBadRequest, JsonResponse
from django.core.exceptions import ValidationError

from rest_framework import generics, permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView

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
    queryset = get_user_model().objects.all()
    serializer_class = serializers.UserSerializer


# GET / PUT / PATCH
class UserDetail(generics.RetrieveUpdateAPIView):
    queryset = get_user_model().objects.all()
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
    queryset = models.Quote.objects.all()
    serializer_class = serializers.QuoteSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


# GET / PUT / PATCH
class QuoteDetail(generics.RetrieveUpdateAPIView):
    queryset = models.Quote.objects.all()
    serializer_class = serializers.QuoteSerializer
    owner_obj_field = 'author'
    permission_classes = (
        permissions.IsAuthenticated,
        custom_permissions.IsOwnerOrReadOnly,
    )


# POST
class QuoteVote(APIView):

    def post(self, request, pk):
        quote = get_object_or_404(models.Quote, pk=pk)
        vote = request.POST.get('vote')

        if vote not in ['up', 'down', 'remove']:
            return HttpResponseBadRequest('Expected up/down/remove for vote')

        if vote == 'remove':
            models.QuoteVote.objects.get(user=request.user, quote=quote).delete()
        else:
            try:
                vote_obj = models.QuoteVote.objects.get(
                    user=request.user, quote=quote)
            except models.QuoteVote.DoesNotExist:
                vote_obj = models.QuoteVote()
                vote_obj.user = request.user
                vote_obj.quote = quote
            vote_obj.vote = vote == 'up'
            vote_obj.save()

        data = {
            'quote_pk': quote.pk,
            'vote': vote,
            'vote_count': quote.QuoteVote.count(),
            'vote_sum': quote.vote_sum()
        }
        return JsonResponse(data)


# POST
class LecturerRate(APIView):

    def post(self, request, pk):
        lecturer = get_object_or_404(models.Lecturer, pk=pk)
        score = request.POST.get('score')
        category = request.POST.get('category')

        params = {
            'user': request.user,
            'lecturer_id': lecturer.pk,
            'category': category,
        }
        try:
            rating = models.LecturerRating.objects.get(**params)
        except models.LecturerRating.DoesNotExist:
            rating = models.LecturerRating(**params)

        rating.rating = score
        try:
            rating.full_clean()  # validation
        except ValidationError:
            return HttpResponseBadRequest('Validierungsfehler')

        rating.save()

        data = {
            'category': category,
            'rating_avg': lecturer._avg_rating(category),
            'rating_count': lecturer._rating_count(category),
        }
        return JsonResponse(data)
