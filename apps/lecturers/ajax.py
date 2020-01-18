import json

from django.core.exceptions import ValidationError
from dajaxice.decorators import dajaxice_register

from apps.lecturers import models


class AuthenticationRequiredError(RuntimeError):
    pass
