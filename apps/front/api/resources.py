from tastypie.resources import ModelResource
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.authentication import ApiKeyAuthentication
from tastypie.authorization import ReadOnlyAuthorization
from tastypie import fields
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from apps.front import models


class BaseMeta:
    allowed_methods = ['get']
    authentication = ApiKeyAuthentication()
    authorization = ReadOnlyAuthorization()


class UsersResource(ModelResource):
    twitter = fields.CharField(readonly=True, attribute='profile__twitter')
    flattr = fields.CharField(readonly=True, attribute='profile__flattr')

    class Meta(BaseMeta):
        queryset = User.objects.all()
        excludes = ['email', 'is_active', 'is_staff', 'is_superuser', 'last_login', 'password']
        filtering = {
            'first_name': ALL,
            'last_name': ALL,
            'username': ALL,
        }


class LecturersResource(ModelResource):
    photo = fields.CharField(readonly=True, attribute='photo')
    avg_rating_d = fields.IntegerField(readonly=True, attribute='avg_rating_d')
    avg_rating_m = fields.IntegerField(readonly=True, attribute='avg_rating_m')
    avg_rating_f = fields.IntegerField(readonly=True, attribute='avg_rating_f')

    class Meta(BaseMeta):
        queryset = models.Lecturer.objects.all()
        filtering = {
            'abbreviation': ALL,
            'department': ALL,
            'first_name': ALL,
            'last_name': ALL,
            'function': ALL,
            'office': ALL,
            'title': ALL,
        }


class QuotesResource(ModelResource):
    author = fields.ToOneField(UsersResource, 'author')
    lecturer = fields.ToOneField(LecturersResource, 'lecturer')

    class Meta(BaseMeta):
        queryset = models.Quote.objects.all()
        filtering = {
            'author': ALL_WITH_RELATIONS,
            'lecturer': ALL_WITH_RELATIONS,
            'date': ALL,
        }

    def dehydrate_date(self, bundle):
        """If date is 01-01-1970, return null."""
        if bundle.obj.date_available():
            return bundle.obj.date
        return None


class QuoteVotesResource(ModelResource):
    user = fields.ToOneField(UsersResource, 'user')
    quote = fields.ToOneField(QuotesResource, 'quote')

    class Meta(BaseMeta):
        queryset = models.QuoteVote.objects.all()
        filtering = {
            'user': ALL_WITH_RELATIONS,
            'quote': ALL_WITH_RELATIONS,
            'vote': ALL,
        }


class DocumentCategoriesResource(ModelResource):
    documents = fields.ToManyField('apps.front.api.resources.DocumentsResource', 'Document')
    summary_count = fields.IntegerField(readonly=True, attribute='summary_count')
    exam_count = fields.IntegerField(readonly=True, attribute='exam_count')

    class Meta(BaseMeta):
        queryset = models.DocumentCategory.objects.all()
        filtering = {
            'name': ALL,
            'description': ALL,
        }


class DocumentsResource(ModelResource):
    category = fields.ToOneField(DocumentCategoriesResource, 'category')
    category_name = fields.CharField(readonly=True)
    uploader = fields.ToOneField(UsersResource, 'uploader', null=True)
    rating = fields.IntegerField(readonly=True, attribute='rating')
    rating_exact = fields.FloatField(readonly=True, attribute='rating_exact')
    dtype_name = fields.CharField(readonly=True)
    document_uri = fields.CharField(readonly=True)
    downloadcount = fields.IntegerField(readonly=True, attribute='downloadcount')

    class Meta(BaseMeta):
        queryset = models.Document.objects.all()
        excludes = ['document']
        filtering = {
            'name': ALL,
            'dtype': ALL,
            'category': ALL_WITH_RELATIONS,
            'uploader': ALL_WITH_RELATIONS,
            'upload_date': ALL,
        }

    def dehydrate_category_name(self, bundle):
        return bundle.obj.category.name

    def dehydrate_dtype_name(self, bundle):
        return bundle.obj.get_dtype_display()

    def dehydrate_document_uri(self, bundle):
        if bundle.obj.exists():
            return reverse('document_download', kwargs={
                'category': slugify(bundle.obj.category.name),
                'pk': bundle.obj.pk
            })
        return None


class EventsResource(ModelResource):
    author = fields.ToOneField(UsersResource, 'author', null=True)
    is_over = fields.BooleanField(readonly=True, attribute='is_over')
    all_day = fields.BooleanField(readonly=True, attribute='all_day')
    days_until = fields.IntegerField(readonly=True, attribute='days_until')

    class Meta(BaseMeta):
        queryset = models.Event.objects.all()
        filtering = {
            'summary': ALL,
            'author': ALL_WITH_RELATIONS,
            'start_date': ALL,
            'start_time': ALL,
            'end_date': ALL,
            'end_time': ALL,
        }
