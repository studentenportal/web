from django.contrib import admin

from apps.lecturers import models


class QuoteAdmin(admin.ModelAdmin):
    list_filter = ("author", "lecturer")


admin.site.register(models.Course)
admin.site.register(models.Lecturer)
admin.site.register(models.LecturerRating)
admin.site.register(models.Quote, QuoteAdmin)
admin.site.register(models.QuoteVote)
