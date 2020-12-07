# -*- coding: utf-8 -*-
"""Helper functions."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)


def extend_quotes_with_votes(quotes, user_pk):
    """Extends a quote queryset with quote votes (using an extra()-query)."""

    vote_base_query = "SELECT EXISTS (SELECT id \
            FROM lecturers_quotevote \
            WHERE lecturers_quotevote.quote_id = lecturers_quote.id \
            AND vote = '%s' \
            AND user_id = %u)"
    count_query = "SELECT COUNT(*) \
            FROM lecturers_quotevote \
            WHERE lecturers_quotevote.quote_id = lecturers_quote.id"
    count_base_query = count_query + " AND vote = '%s'"

    return quotes.extra(
        select={
            "voted_up": vote_base_query % ("t", user_pk),
            "voted_down": vote_base_query % ("f", user_pk),
            "vote_count": count_query,
            "upvote_count": count_base_query % "t",
            "downvote_count": count_base_query % "f",
        },
    )
