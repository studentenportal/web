from django.contrib.auth import get_user_model
from model_bakery.recipe import Recipe

User = get_user_model()
user = Recipe(
    User,
    username="testuser",
    password="pbkdf2_sha256$36000$pFltpNNB0Q2H$zd9qOeVuvJUzaxeELpx/Bn10Fgsoq50QDdCljAFNZ58=",
    email="test@studentenportal.ch",
)
