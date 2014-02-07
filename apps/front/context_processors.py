from apps.front import models
from apps.lecturers import models as lecturers_models


def global_stats(request):
    """This context processor adds global stats to each context."""
    return {
        'usercount': models.User.objects.count(),
        'lecturercount': lecturers_models.Lecturer.real_objects.count(),
        'documentcount': models.Document.objects.count(),
        'quotecount': lecturers_models.Quote.objects.count(),
    }
