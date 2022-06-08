from django.db import models
from django.utils.translation import gettext_lazy as _


class CaseInsensitiveSlugField(models.SlugField):
    """
    A SlugField that uses the PostgreSQL CITEXT type for
    case insensitive comparison.
    """

    description = _(
        "A SlugField that uses the PostgreSQL CITEXT type for \
                     case insensitive comparison."
    )

    def db_type(self, connection):
        return "CITEXT"
