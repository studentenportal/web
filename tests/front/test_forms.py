import pytest

from apps.front import forms


@pytest.mark.parametrize(
    "username, valid",
    [
        ("m.mueller", True),
        ("m.muel_ler", True),
        ("m.muel-ler", True),
        ("m.2mueller", True),
        ("a.+++", False),
    ],
)
def test_username_regex(username, valid):
    assert bool(forms.USERNAME_REGEX.match(username)) == valid
