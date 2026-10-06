from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.documents import models as doc_models
from apps.events import models as event_models
from apps.lecturers import models as lecturer_models
from apps.tipps import models as tipp_models


class UserListSerializer(serializers.ModelSerializer):
    """Public user data. Sensitive data (email) is not included."""

    quotes = serializers.PrimaryKeyRelatedField(
        many=True, read_only=True, source="Quote"
    )

    class Meta:
        model = get_user_model()
        fields = ("id", "username", "first_name", "last_name", "quotes")


class UserSerializer(UserListSerializer):
    """Full user data. Only used for a user's own profile, so the
    sensitive email field may be included. The email cannot be changed
    through the API (see ProfileForm)."""

    username = serializers.ReadOnlyField()
    email = serializers.EmailField(read_only=True)

    class Meta(UserListSerializer.Meta):
        fields = UserListSerializer.Meta.fields + ("email",)


class LecturerSerializer(serializers.ModelSerializer):
    quotes = serializers.PrimaryKeyRelatedField(
        many=True, read_only=True, source="Quote"
    )

    class Meta:
        model = lecturer_models.Lecturer
        fields = (
            "id",
            "title",
            "last_name",
            "first_name",
            "abbreviation",
            "department",
            "function",
            "main_area",
            "subjects",
            "email",
            "office",
            "quotes",
        )


class QuoteSerializer(serializers.ModelSerializer):
    lecturer = serializers.PrimaryKeyRelatedField(
        queryset=lecturer_models.Lecturer.objects.all()
    )
    lecturer_name = serializers.ReadOnlyField(source="lecturer.name")
    votes = serializers.ReadOnlyField(source="vote_sum")

    class Meta:
        model = lecturer_models.Quote
        fields = (
            "id",
            "lecturer",
            "lecturer_name",
            "date",
            "quote",
            "comment",
            "votes",
        )
        read_only_fields = ("date",)


class DocumentCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = doc_models.DocumentCategory
        fields = ("id", "name", "description")


class DocumentSerializer(serializers.ModelSerializer):
    uploader = serializers.PrimaryKeyRelatedField(read_only=True)
    original_filename = serializers.ReadOnlyField()
    change_date = serializers.ReadOnlyField()
    rating = serializers.SerializerMethodField()
    rating_count = serializers.SerializerMethodField()
    download_count = serializers.SerializerMethodField()
    file_size = serializers.SerializerMethodField()

    class Meta:
        model = doc_models.Document
        fields = (
            "id",
            "name",
            "description",
            "url",
            "category",
            "dtype",
            "document",
            "original_filename",
            "uploader",
            "upload_date",
            "change_date",
            "license",
            "public",
            "rating",
            "rating_count",
            "download_count",
            "file_size",
        )

    def get_rating(self, obj):
        return obj.rating()

    def get_rating_count(self, obj):
        return obj.DocumentRating.count()

    def get_download_count(self, obj):
        return obj.downloadcount()

    def get_file_size(self, obj):
        try:
            return obj.document.size
        except (ValueError, OSError):
            return None

    def validate(self, attrs):
        # Same rule as the website form: exams may not be public
        if attrs.get("dtype") == doc_models.Document.DTypes.EXAM and attrs.get(
            "public"
        ):
            raise serializers.ValidationError(
                {"public": "Prüfungen dürfen nicht öffentlich sein."}
            )
        return attrs


class EventSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = event_models.Event
        fields = (
            "id",
            "author",
            "summary",
            "description",
            "start_date",
            "start_time",
            "end_date",
            "end_time",
            "repeats",
            "repeat_every",
            "repeat_unit",
            "repeat_ends",
            "location",
            "url",
            "picture",
        )

    def validate(self, attrs):
        # Same rule as the website form
        if attrs.get("repeats") and (
            not attrs.get("repeat_every")
            or attrs.get("repeat_unit") is None
            or attrs.get("repeat_ends") is None
        ):
            raise serializers.ValidationError(
                'Für wiederholende Events müssen "Alle" (>0), "Einheit" '
                'und "Wiederholungsende" angegeben werden.'
            )
        return attrs


class TippSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(read_only=True)
    votes = serializers.ReadOnlyField(source="vote_sum")
    comment_count = serializers.SerializerMethodField()

    class Meta:
        model = tipp_models.Tipp
        fields = (
            "id",
            "author",
            "summary",
            "description",
            "date",
            "votes",
            "comment_count",
        )
        read_only_fields = ("date",)

    def get_comment_count(self, obj):
        return obj.comments.count()


class TippCommentSerializer(serializers.ModelSerializer):
    tipp = serializers.PrimaryKeyRelatedField(read_only=True)
    author = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = tipp_models.TippComment
        fields = ("id", "tipp", "author", "text", "date")
        read_only_fields = ("date",)
