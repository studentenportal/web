from registration.backends.default import DefaultBackend
from apps.front.forms import HsrRegistrationForm

class HsrEmailBackend(DefaultBackend):
    """An extension of the DefaultBackend, that requires
    a HSR e-mail address.

    It does this, by requiring only the HSR username and generating the
    e-mail address from it.
    
    """
    def get_form_class(self, request):
        return HsrRegistrationForm

    def register(self, request, **kwargs):
        username = kwargs['username'].lower()
        kwargs['email'] = '%s@hsr.ch' % username
        return super(HsrEmailBackend, self).register(request, **kwargs)
