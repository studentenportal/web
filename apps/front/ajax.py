from django.utils import simplejson
from dajaxice.decorators import dajaxice_register
from apps.front import models

@dajaxice_register
def vote_quote(request, vote, quote_pk):
    quote = models.Quote.objects.get(pk=quote_pk)
    if vote in ('up', 'down'):
        vote_obj, _ = models.QuoteVote.objects.get_or_create(user=request.user, quote=quote)
        vote_obj.vote = vote == 'up'
        vote_obj.save()
    elif vote == 'remove':
        models.QuoteVote.objects.get(user=request.user, quote=quote).delete()
    return simplejson.dumps({'quote_pk': quote_pk, 'vote': vote, 'vote_sum': quote.vote_sum()})
