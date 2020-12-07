# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from apps.front import models
from apps.lecturers import models as lecturer_models
from apps.documents import models as document_models
from django.conf import settings


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
