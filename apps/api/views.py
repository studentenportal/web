from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import filters, generics, permissions
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView

from apps.documents import models as doc_models
from apps.events import models as event_models
from apps.front.voting import VoteViewMixin
from apps.lecturers import models
from apps.tipps import models as tipp_models

from . import permissions as custom_permissions
from . import serializers


class QSearchFilter(filters.SearchFilter):
    """SearchFilter that reads the search term from ?q= (site convention)."""

    search_param = "q"


class ApiRoot(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, format=None):
        return Response(
            {
                "users": reverse("api:user_list", request=request, format=format),
                "lecturers": reverse(
                    "api:lecturer_list", request=request, format=format
                ),
                "quotes": reverse("api:quote_list", request=request, format=format),
                "documents": reverse(
                    "api:document_list", request=request, format=format
                ),
                "documentcategories": reverse(
                    "api:documentcategory_list", request=request, format=format
                ),
                "events": reverse("api:event_list", request=request, format=format),
                "tipps": reverse("api:tipp_list", request=request, format=format),
            }
        )


# GET
class UserList(generics.ListAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = serializers.UserListSerializer
    filter_backends = (QSearchFilter, filters.OrderingFilter)
    search_fields = ("username", "email")
    ordering_fields = ("username",)
    ordering = ("username",)


# GET / PUT / PATCH
class UserDetail(generics.RetrieveUpdateAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = serializers.UserListSerializer
    owner_username_field = "username"
    permission_classes = (
        permissions.IsAuthenticated,
        custom_permissions.IsOwnerOrReadOnly,
    )

    def get_serializer_class(self):
        # Only include sensitive data (email) in one's own profile
        if str(self.request.user.pk) == self.kwargs.get("pk"):
            return serializers.UserSerializer
        return serializers.UserListSerializer


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


# GET / PUT / PATCH / DELETE
class QuoteDetail(generics.RetrieveUpdateDestroyAPIView):
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


class DocumentCategoryList(generics.ListCreateAPIView):
    queryset = doc_models.DocumentCategory.objects.all()
    serializer_class = serializers.DocumentCategorySerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    filter_backends = (QSearchFilter, filters.OrderingFilter)
    search_fields = ("name", "description")
    ordering_fields = ("name",)
    ordering = ("name",)


class DocumentCategoryDetail(generics.RetrieveAPIView):
    queryset = doc_models.DocumentCategory.objects.all()
    serializer_class = serializers.DocumentCategorySerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class DocumentList(generics.ListCreateAPIView):
    serializer_class = serializers.DocumentSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    filter_backends = (QSearchFilter, filters.OrderingFilter)
    search_fields = ("name", "description")
    ordering_fields = ("upload_date", "change_date", "name")
    ordering = ("-upload_date",)

    def get_queryset(self):
        # Anonymous users only see public documents
        queryset = doc_models.Document.objects.all()
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(public=True)
        return queryset

    def perform_create(self, serializer):
        serializer.save(uploader=self.request.user)


class DocumentDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.DocumentSerializer
    owner_obj_field = "uploader"
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        custom_permissions.IsOwnerOrReadOnly,
    )

    def get_queryset(self):
        # Anonymous users only see public documents
        queryset = doc_models.Document.objects.all()
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(public=True)
        return queryset

    def perform_update(self, serializer):
        """Set change_date when the uploaded document is replaced."""
        instance = serializer.save()
        if "document" in self.request.data:
            instance.change_date = timezone.now()
            instance.save(update_fields=["change_date"])


class DocumentRate(APIView):
    def post(self, request, pk):
        document = get_object_or_404(doc_models.Document, pk=pk)
        score = request.POST.get("score")
        if not score:
            return HttpResponseBadRequest("Required argument missing")

        params = {
            "user": request.user,
            "document": document,
        }
        try:
            rating = doc_models.DocumentRating.objects.get(**params)
        except doc_models.DocumentRating.DoesNotExist:
            rating = doc_models.DocumentRating(**params)

        rating.rating = score
        try:
            rating.full_clean()  # validation
        except ValidationError:
            return HttpResponseBadRequest("Validierungsfehler")

        rating.save()

        data = {
            "rating": int(score),
            "rating_avg": document.rating(),
            "rating_count": document.DocumentRating.count(),
        }
        return JsonResponse(data)


class EventList(generics.ListCreateAPIView):
    queryset = event_models.Event.objects.all()
    serializer_class = serializers.EventSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    filter_backends = (QSearchFilter, filters.OrderingFilter)
    search_fields = ("summary", "description", "location")
    ordering_fields = ("start_date", "summary")
    ordering = ("start_date",)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class EventDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = event_models.Event.objects.all()
    serializer_class = serializers.EventSerializer
    owner_obj_field = "author"
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        custom_permissions.IsOwnerOrReadOnly,
    )


class TippList(generics.ListCreateAPIView):
    queryset = tipp_models.Tipp.objects.all()
    serializer_class = serializers.TippSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    filter_backends = (QSearchFilter, filters.OrderingFilter)
    search_fields = ("summary", "description")
    ordering_fields = ("date",)
    ordering = ("-date",)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class TippDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = tipp_models.Tipp.objects.all()
    serializer_class = serializers.TippSerializer
    owner_obj_field = "author"
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        custom_permissions.IsOwnerOrReadOnly,
    )


# POST
class TippVote(VoteViewMixin):
    item_model = tipp_models.Tipp
    vote_model = tipp_models.TippVote
    item_fk_name = "tipp"


class TippCommentList(generics.ListCreateAPIView):
    serializer_class = serializers.TippCommentSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        tipp = get_object_or_404(tipp_models.Tipp, pk=self.kwargs["tpk"])
        return tipp.comments.all()

    def perform_create(self, serializer):
        tipp = get_object_or_404(tipp_models.Tipp, pk=self.kwargs["tpk"])
        serializer.save(tipp=tipp, author=self.request.user)


class TippCommentDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.TippCommentSerializer
    owner_obj_field = "author"
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        custom_permissions.IsOwnerOrReadOnly,
    )

    def get_queryset(self):
        tipp = get_object_or_404(tipp_models.Tipp, pk=self.kwargs["tpk"])
        return tipp.comments.all()
