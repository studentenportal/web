# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("lecturers", "0001_initial"),
        ("documents", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="documentrating",
            name="user",
            field=models.ForeignKey(
                related_name="DocumentRating",
                to=settings.AUTH_USER_MODEL,
                on_delete=django.db.models.deletion.CASCADE,
            ),
        ),
        migrations.AddField(
            model_name="documentdownload",
            name="document",
            field=models.ForeignKey(
                related_name="DocumentDownload",
                to="documents.Document",
                on_delete=django.db.models.deletion.CASCADE,
            ),
        ),
        migrations.AddField(
            model_name="documentcategory",
            name="courses",
            field=models.ManyToManyField(to="lecturers.Course", blank=True),
        ),
        migrations.AddField(
            model_name="documentcategory",
            name="lecturers",
            field=models.ManyToManyField(to="lecturers.Lecturer", blank=True),
        ),
        migrations.AddField(
            model_name="document",
            name="category",
            field=models.ForeignKey(
                related_name="Document",
                on_delete=django.db.models.deletion.PROTECT,
                verbose_name="Modul",
                to="documents.DocumentCategory",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="document",
            name="uploader",
            field=models.ForeignKey(
                related_name="Document",
                on_delete=django.db.models.deletion.SET_NULL,
                to=settings.AUTH_USER_MODEL,
                null=True,
            ),
        ),
        migrations.AlterUniqueTogether(
            name="documentrating",
            unique_together={("user", "document")},
        ),
        migrations.AlterIndexTogether(
            name="documentdownload",
            index_together={("document", "timestamp", "ip")},
        ),
    ]
