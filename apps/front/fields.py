from django.db import models
from django.utils.translation import ugettext_lazy as _
from south.modelsinspector import add_introspection_rules


class CaseInsensitiveSlugField(models.SlugField):
    """
    A SlugField that uses the PostgreSQL CITEXT type for
    case insensitive comparison.
    """
    description = _("A SlugField that uses the PostgreSQL CITEXT type for \
                     case insensitive comparison.")
    db_type = lambda self, connection: 'CITEXT'


add_introspection_rules([], ["^apps\.front\.fields\.CaseInsensitiveSlugField"])
