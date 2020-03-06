# -*- coding: utf-8 -*-

import pytest

from apps.front import forms


@pytest.mark.parametrize('username, valid', [
    ('mmueller', True),
    ('m_mueller', True),
    ('m-mueller', True),
    ('m2mueller', True),
    ('a+++', False),
])
def test_username_re(username, valid):
    assert bool(forms.USERNAME_RE.match(username)) == valid
