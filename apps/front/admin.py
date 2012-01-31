from django.contrib import admin
from apps.front import models

admin.site.register(models.Lecturer)
admin.site.register(models.Document)
admin.site.register(models.DocumentCategory)
admin.site.register(models.DocumentRating)
admin.site.register(models.Event)
