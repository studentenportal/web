from django.db import models

class Lecturer(models.Model):
    name = models.CharField(max_length=255)
    abbreviation = models.CharField(max_length=10, unique=True)
