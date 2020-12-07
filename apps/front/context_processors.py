# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from django.conf import settings

from apps.documents import models as document_models
from apps.front import models
from apps.lecturers import models as lecturer_models


def global_stats(request):
    """This context processor adds global stats to each context."""
    return {
        "usercount": models.User.objects.count(),
        "lecturercount": lecturer_models.Lecturer.real_objects.count(),
        "documentcount": document_models.Document.objects.count(),
        "quotecount": lecturer_models.Quote.objects.count(),
    }


def debug(context):
    return {"DEBUG": settings.DEBUG}
