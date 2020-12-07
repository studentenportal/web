# -*- coding: utf-8 -*-
import pytest

from apps.front.templatetags import tags


@pytest.mark.parametrize(
    "arg, expected",
    [
        (0, []),
        (-5, []),
        (5, [0, 1, 2, 3, 4]),
    ],
)
def test_get_range(arg, expected):
    r = tags.get_range(arg)
    assert list(r) == expected


@pytest.mark.parametrize(
    "arg, expected",
    [
        (0, []),
        (1, [1]),
        (-5, []),
        (5, [1, 2, 3, 4, 5]),
    ],
)
def test_get_range1(arg, expected):
    r = tags.get_range1(arg)
    assert list(r) == expected
