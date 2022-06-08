from django.contrib import admin

from apps.events import models

admin.site.register(models.Event)
