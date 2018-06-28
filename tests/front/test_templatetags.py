# -*- coding: utf-8 -*-
from apps.front.templatetags import tags


class GetRangeTest:

    def testZero(self):
        r = tags.get_range(0)
        assert len(r) == 0

    def testNegative(self):
        r = tags.get_range(-5)
        assert len(r) == 0

    def testPositive(self):
        r = tags.get_range(5)
        assert len(r) == 5
        assert r[0] == 0
        assert r[4] == 4


class GetRange1Test:

    def testZero(self):
        r = tags.get_range1(0)
        assert len(r) == 0

    def testOne(self):
        r = tags.get_range1(1)
        assert len(r) == 1
        assert r[0] == 1

    def testNegative(self):
        r = tags.get_range1(-5)
        assert len(r) == 0

    def testPositive(self):
        r = tags.get_range1(5)
        assert len(r) == 5
        assert r[0] == 1
        assert r[4] == 5
