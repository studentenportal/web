# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from django.contrib import admin

from . import models


class DocumentAdmin(admin.ModelAdmin):
    list_filter = ('category', 'uploader')
    search_fields = ('name', 'description')


class DocumentCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = list_display


admin.site.register(models.Document, DocumentAdmin)
admin.site.register(models.DocumentCategory, DocumentCategoryAdmin)
admin.site.register(models.DocumentRating)
