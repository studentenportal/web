# coding=utf-8
import urllib
import requests
import json
from itertools import chain, islice

from django.core.management.base import NoArgsCommand

from apps.front import models


SEARCH_URL = 'http://search.twitter.com/search.json?q='


class Helpers(object):

    @classmethod
    def ichunked(cls, seq, chunksize):
        """Yields items from an iterator in iterable chunks."""
        it = iter(seq)
        while True:
            yield chain([it.next()], islice(it, chunksize-1))

    @classmethod
    def chunked(cls, seq, chunksize):
        """Yields items from an iterator in list chunks."""
        for chunk in cls.ichunked(seq, chunksize):
            yield list(chunk)


class Command(NoArgsCommand):
    help = 'Fetch HSR quotes on twitter'

    def handle_noargs(self, **options):
        """Fetch tweets"""

        queries = []
        abbr = models.Lecturer.objects.values_list('abbreviation', flat=True)
        for chunk in Helpers.ichunked(abbr, 40):
            queries.append('#HSR AND (#%s)' % ' OR #'.join(chunk))

        for query in queries:
            r = requests.get(SEARCH_URL + urllib.quote(query.encode('utf-8')))
            j = json.loads(r.content)
            print j['results']
