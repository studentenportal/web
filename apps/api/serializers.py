# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from rest_framework import serializers

from django.contrib.auth import models as auth_models

from apps.front import models


class UserSerializer(serializers.ModelSerializer):
    Quote = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    flattr = serializers.CharField(source='profile.flattr')
    twitter = serializers.CharField(source='profile.twitter')

    class Meta:
        model = auth_models.User
        fields = ('id', 'username', 'first_name', 'last_name', 'email',
                  'flattr', 'twitter', 'Quote')
        read_only_fields = ('id',)


class LecturerSerializer(serializers.ModelSerializer):
    quotes = serializers.PrimaryKeyRelatedField(many=True)

    class Meta:
        model = models.Lecturer
        fields = ('id', 'title', 'last_name', 'first_name', 'abbreviation',
                'department', 'function', 'main_area', 'subjects', 'email',
                'office')


class QuoteSerializer(serializers.ModelSerializer):
    author = serializers.Field(source='author.username')
    lecturer = serializers.Field()
    quote_votes = serializers.PrimaryKeyRelatedField(many=True)

    class Meta:
        model = models.Quote
        fields = ('id', 'author', 'lecturer', 'date', 'quote', 'comment')
