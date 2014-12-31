from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model


def strip_mail_part(username):
    """
    Users might try to login with their email. To support that
    we can simply strip the mail part from the username
    """
    if '@' in username:
        return username.split('@')[0]
    return username


class CaseInsensitiveModelBackend(ModelBackend):
    """
    By default ModelBackend does case _sensitive_ username authentication, which isn't what is
    generally expected.  This backend supports case insensitive username authentication.

    Source: http://blog.shopfiber.com/?p=220

    """
    def authenticate(self, username=None, password=None):
        username = strip_mail_part(username)
        User = get_user_model()
        try:
            user = User.objects.get(username__iexact=username)
            if user.check_password(password):
                return user
            else:
                return None
        except User.DoesNotExist:
            return None
