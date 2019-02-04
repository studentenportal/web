# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from rest_framework import serializers

from django.contrib.auth import get_user_model

from apps.lecturers import models


class UserSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField()
    quotes = serializers.PrimaryKeyRelatedField(many=True, read_only=True, source='Quote')
    flattr = serializers.CharField(allow_blank=True)
    twitter = serializers.CharField(allow_blank=True)

    class Meta:
        model = get_user_model()
        fields = ('id', 'username', 'first_name', 'last_name', 'email',
                  'flattr', 'twitter', 'quotes')


class LecturerSerializer(serializers.ModelSerializer):
    quotes = serializers.PrimaryKeyRelatedField(many=True, read_only=True, source='Quote')

    class Meta:
        model = models.Lecturer
        fields = ('id', 'title', 'last_name', 'first_name', 'abbreviation',
                  'department', 'function', 'main_area', 'subjects', 'email',
                  'office', 'quotes')


class QuoteSerializer(serializers.ModelSerializer):
    lecturer = serializers.PrimaryKeyRelatedField(queryset=models.Lecturer.objects.all())
    lecturer_name = serializers.ReadOnlyField(source='lecturer.name')

    class Meta:
        model = models.Quote
        fields = ('id', 'lecturer', 'lecturer_name', 'date', 'quote', 'comment')
