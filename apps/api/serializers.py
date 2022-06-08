from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.lecturers import models


class UserSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField()
    quotes = serializers.PrimaryKeyRelatedField(
        many=True, read_only=True, source="Quote"
    )

    class Meta:
        model = get_user_model()
        fields = ("id", "username", "first_name", "last_name", "email", "quotes")


class LecturerSerializer(serializers.ModelSerializer):
    quotes = serializers.PrimaryKeyRelatedField(
        many=True, read_only=True, source="Quote"
    )

    class Meta:
        model = models.Lecturer
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
        queryset=models.Lecturer.objects.all()
    )
    lecturer_name = serializers.ReadOnlyField(source="lecturer.name")
    votes = serializers.ReadOnlyField(source="vote_sum")

    class Meta:
        model = models.Quote
        fields = (
            "id",
            "lecturer",
            "lecturer_name",
            "date",
            "quote",
            "comment",
            "votes",
        )
