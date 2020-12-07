# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model

from model_bakery import baker

from apps.api import serializers


@pytest.mark.django_db
def test_serialization():
    """A simple serialization test case."""
    user = baker.make(get_user_model())
    serializer = serializers.UserSerializer(user)
    data = serializer.data
    assert data == {
        "id": user.pk,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "quotes": [],
    }
