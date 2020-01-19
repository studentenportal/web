# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from django.contrib.auth import get_user_model

from model_bakery.recipe import Recipe


User = get_user_model()
user = Recipe(User,
    username='testuser',
    password='sha1$4b2d5$c6ff8b2ff002131f58cfb0a5b43a6681a0b723b3',
    email='test@studentenportal.ch',
)
