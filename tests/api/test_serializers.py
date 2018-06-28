# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

import pytest
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model

from model_mommy import mommy

from apps.api import serializers


@pytest.mark.django_db
def test_serialization():
    """A simple serialization test case."""
    user = mommy.make(get_user_model(), flattr='flttr', twitter='twttr')
    serializer = serializers.UserSerializer(user)
    data = serializer.data
    url = reverse('api:user_detail', args=(user.pk,))
    assert data == {
        'url': url,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'flattr': 'flttr',
        'twitter': 'twttr'
    }
