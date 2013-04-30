# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from rest_framework import serializers

from django.contrib.auth import get_user_model

from apps.front import models


class UserSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='api:user_detail')
    username = serializers.Field()
    quotes = serializers.HyperlinkedRelatedField(many=True, read_only=True, source='Quote',
            view_name='api:quote_detail')
    flattr = serializers.CharField(source='flattr', blank=True)
    twitter = serializers.CharField(source='twitter', blank=True)

    class Meta:
        model = get_user_model()
        fields = ('url', 'username', 'first_name', 'last_name', 'email',
                  'flattr', 'twitter')


class LecturerSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='api:lecturer_detail')
    quotes = serializers.HyperlinkedRelatedField(many=True, read_only=True, source='Quote',
            view_name='api:quote_detail')

    class Meta:
        model = models.Lecturer
        fields = ('url', 'title', 'last_name', 'first_name', 'abbreviation',
                  'department', 'function', 'main_area', 'subjects', 'email',
                  'office', 'quotes')


class QuoteSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='api:quote_detail')
    lecturer = serializers.HyperlinkedRelatedField(view_name='api:lecturer_detail')
    lecturer_name = serializers.Field(source='lecturer.name')
    quote_votes = serializers.PrimaryKeyRelatedField(many=True)

    class Meta:
        model = models.Quote
        fields = ('url', 'lecturer', 'lecturer_name', 'date', 'quote', 'comment')
