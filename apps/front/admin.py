from tastypie.admin import ApiKeyInline
from tastypie.models import ApiAccess, ApiKey
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from apps.front import models

class QuoteAdmin(admin.ModelAdmin):
    list_filter = ('author', 'lecturer')

class DocumentCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'description')

class DocumentAdmin(admin.ModelAdmin):
    list_filter = ('category', 'uploader')
    search_fields = ('name', 'description')

class UserAdmin(UserAdmin):
    inlines = UserAdmin.inlines + [ApiKeyInline]
    search_fields = ('username', 'first_name', 'last_name', 'email')

admin.site.register(models.UserProfile)
admin.site.register(models.Lecturer)
admin.site.register(models.LecturerRating)
admin.site.register(models.Quote, QuoteAdmin)
admin.site.register(models.QuoteVote)
admin.site.register(models.Document, DocumentAdmin)
admin.site.register(models.DocumentCategory, DocumentCategoryAdmin)
admin.site.register(models.DocumentRating)
admin.site.register(models.Event)
admin.site.register(ApiKey)
admin.site.register(ApiAccess)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
