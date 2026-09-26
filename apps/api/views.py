from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import filters, generics, permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView

from apps.front.voting import VoteViewMixin
from apps.lecturers import models

from . import permissions as custom_permissions
from . import serializers


class QSearchFilter(filters.SearchFilter):
    """SearchFilter that reads the search term from ?q= (site convention)."""

    search_param = "q"


@api_view(("GET",))
def api_root(request, format=None):
    return Response(
        {
            "users": reverse("api:user_list", request=request, format=format),
            "lecturers": reverse("api:lecturer_list", request=request, format=format),
            "quotes": reverse("api:quote_list", request=request, format=format),
        }
    )


# GET
class UserList(generics.ListAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = serializers.UserSerializer
    filter_backends = (QSearchFilter, filters.OrderingFilter)
    search_fields = ("username", "email")
    ordering_fields = ("username",)
    ordering = ("username",)


# GET / PUT / PATCH
class UserDetail(generics.RetrieveUpdateAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = serializers.UserSerializer
    owner_username_field = "username"
    permission_classes = (
        permissions.IsAuthenticated,
        custom_permissions.IsOwnerOrReadOnly,
    )


# GET
class LecturerList(generics.ListAPIView):
    queryset = models.Lecturer.real_objects.all()
    serializer_class = serializers.LecturerSerializer
    filter_backends = (QSearchFilter, filters.OrderingFilter)
    search_fields = ("first_name", "last_name", "abbreviation")
    ordering_fields = ("last_name", "first_name")
    ordering = ("last_name", "first_name")


# GET
class LecturerDetail(generics.RetrieveAPIView):
    queryset = models.Lecturer.real_objects.all()
    serializer_class = serializers.LecturerSerializer


# GET / POST
class QuoteList(generics.ListCreateAPIView):
    queryset = models.Quote.objects.all()
    serializer_class = serializers.QuoteSerializer
    filter_backends = (QSearchFilter, filters.OrderingFilter)
    search_fields = ("quote", "comment", "lecturer__last_name")
    ordering_fields = ("date",)
    ordering = ("-date",)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


# GET / PUT / PATCH
class QuoteDetail(generics.RetrieveUpdateAPIView):
    queryset = models.Quote.objects.all()
    serializer_class = serializers.QuoteSerializer
    owner_obj_field = "author"
    permission_classes = (
        permissions.IsAuthenticated,
        custom_permissions.IsOwnerOrReadOnly,
    )


# POST
class QuoteVote(VoteViewMixin):
    item_model = models.Quote
    vote_model = models.QuoteVote
    item_fk_name = "quote"


# POST
class LecturerRate(APIView):
    def post(self, request, pk):
        lecturer = get_object_or_404(models.Lecturer, pk=pk)
        score = request.POST.get("score")
        category = request.POST.get("category")

        params = {
            "user": request.user,
            "lecturer_id": lecturer.pk,
            "category": category,
        }
        try:
            rating = models.LecturerRating.objects.get(**params)
        except models.LecturerRating.DoesNotExist:
            rating = models.LecturerRating(**params)

        rating.rating = score
        try:
            rating.full_clean()  # validation
        except ValidationError:
            return HttpResponseBadRequest("Validierungsfehler")

        rating.save()

        data = {
            "category": category,
            "rating_avg": lecturer._avg_rating(category),
            "rating_count": lecturer._rating_count(category),
        }
        return JsonResponse(data)
