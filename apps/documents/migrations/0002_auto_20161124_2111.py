# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('lecturers', '0001_initial'),
        ('documents', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='documentrating',
            name='user',
            field=models.ForeignKey(related_name='DocumentRating', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='documentdownload',
            name='document',
            field=models.ForeignKey(related_name='DocumentDownload', to='documents.Document'),
        ),
        migrations.AddField(
            model_name='documentcategory',
            name='courses',
            field=models.ManyToManyField(to='lecturers.Course', blank=True),
        ),
        migrations.AddField(
            model_name='documentcategory',
            name='lecturers',
            field=models.ManyToManyField(to='lecturers.Lecturer', blank=True),
        ),
        migrations.AddField(
            model_name='document',
            name='category',
            field=models.ForeignKey(related_name='Document', on_delete=django.db.models.deletion.PROTECT, verbose_name='Modul', to='documents.DocumentCategory', null=True),
        ),
        migrations.AddField(
            model_name='document',
            name='uploader',
            field=models.ForeignKey(related_name='Document', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterUniqueTogether(
            name='documentrating',
            unique_together=set([('user', 'document')]),
        ),
        migrations.AlterIndexTogether(
            name='documentdownload',
            index_together=set([('document', 'timestamp', 'ip')]),
        ),
    ]
