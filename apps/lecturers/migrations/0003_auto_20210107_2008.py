# Generated by Django 2.2.17 on 2021-01-07 20:08

from django.db import migrations, models

import apps.lecturers.models


class Migration(migrations.Migration):
    dependencies = [
        ("lecturers", "0002_auto_20201130_1115"),
    ]

    operations = [
        migrations.AddField(
            model_name="lecturer",
            name="picture",
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to=apps.lecturers.models.lecturer_directory_path,
                verbose_name="Bild",
            ),
        ),
        migrations.AlterField(
            model_name="lecturer",
            name="id",
            field=models.AutoField(
                primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
    ]
