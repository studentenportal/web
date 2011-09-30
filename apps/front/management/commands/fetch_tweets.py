import urllib2
from django.core.management.base import NoArgsCommand


SEARCH_URL = 'http://search.twitter.com/search.json?q='
MODULES = [


class Command(NoArgsCommand):
    help = 'Fetch hsr quotes on twitter'

    def handle_noargs(self, **options):
        """Fetch tweets
