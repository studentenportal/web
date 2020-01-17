import json

from django.core.exceptions import ValidationError
from dajaxice.decorators import dajaxice_register

from apps.lecturers import models


class AuthenticationRequiredError(RuntimeError):
    pass


@dajaxice_register
def rate_lecturer(request, lecturer_pk, category, score):

    # Check authentication
    if not request.user.is_authenticated:
        raise AuthenticationRequiredError()

    lecturer = models.Lecturer.objects.get(pk=lecturer_pk)

    params = {
        'user': request.user,
        'lecturer_id': lecturer.pk,
        'category': category,
    }

    try:
        rating = models.LecturerRating.objects.get(**params)
    except models.LecturerRating.DoesNotExist:
        rating = models.LecturerRating(**params)
    rating.rating = score
    try:
        rating.full_clean()  # validation
    except ValidationError:
        return ValueError('Validierungsfehler')
    rating.save()

    return json.dumps({
        'category': category,
        'rating_avg': lecturer._avg_rating(category),
        'rating_count': lecturer._rating_count(category),
    })
