# -*- coding: utf-8 -*-

import pytest

from apps.front import forms


class TestUsernameRegex:

    @pytest.mark.parametrize('username, valid', [
        ('mmueller', True),
        ('m_mueller', True),
        ('m-mueller', True),
        ('m2mueller', True),
        ('a+++', False),
    ])
    @pytest.mark.parametrize('domain', ['hsr.ch', 'ost.ch'])
    def test_common(self, domain, username, valid):
        username_re = forms.USERNAME_REGEXES[domain]
        assert bool(username_re.match(username)) == valid

    @pytest.mark.parametrize('domain, dots_allowed', [
        ('hsr.ch', False),
        ('ost.ch', True),
    ])
    def test_dots(self, domain, dots_allowed):
        username_re = forms.USERNAME_REGEXES[domain]
        assert bool(username_re.match('melanie.mueller')) == dots_allowed
