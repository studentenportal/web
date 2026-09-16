from django.contrib import admin

from apps.tipps import models


@admin.register(models.Tipp)
class TippAdmin(admin.ModelAdmin):
    pass


@admin.register(models.TippComment)
class TippCommentAdmin(admin.ModelAdmin):
    list_display = ("tipp", "author", "date")
    list_filter = ("date",)
