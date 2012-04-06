from apps.front import models

def global_stats(request):
    """This context processor adds global stats to each context."""
    return {
        'usercount': models.User.objects.count(),
        'lecturercount': models.Lecturer.objects.count(),
        'documentcount': models.Document.objects.count(),
        'quotecount': models.Quote.objects.count(),
    }
