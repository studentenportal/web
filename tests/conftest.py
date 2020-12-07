import pytest

from django.contrib.auth import get_user_model


User = get_user_model()  # FIXME use fixture?


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="testuser", password="test", email="test@studentenportal.ch"
    )


@pytest.fixture
def auth_client(client, user):
    assert client.login(username="testuser", password="test")
    return client
