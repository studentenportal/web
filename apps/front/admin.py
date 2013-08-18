# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from django.contrib import admin

from apps.front import models


class QuoteAdmin(admin.ModelAdmin):
    list_filter = ('author', 'lecturer')


class DocumentCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'description')


class DocumentAdmin(admin.ModelAdmin):
    list_filter = ('category', 'uploader')
    search_fields = ('name', 'description')


admin.site.register(models.User)
admin.site.register(models.Lecturer)
admin.site.register(models.LecturerRating)
admin.site.register(models.Quote, QuoteAdmin)
admin.site.register(models.QuoteVote)
admin.site.register(models.Document, DocumentAdmin)
admin.site.register(models.DocumentCategory, DocumentCategoryAdmin)
admin.site.register(models.DocumentRating)
admin.site.register(models.Event)
