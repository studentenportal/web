from apps.front import models
from apps.lecturers.models import Quote, Lecturer


def global_stats(request):
    """This context processor adds global stats to each context."""
    return {
        'usercount': models.User.objects.count(),
        'lecturercount': Lecturer.real_objects.count(),
        'documentcount': models.Document.objects.count(),
        'quotecount': Quote.objects.count(),
    }
