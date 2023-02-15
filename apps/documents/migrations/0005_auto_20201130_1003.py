# Generated by Django 2.2.17 on 2020-11-30 10:03

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("documents", "0004_remove_document_flattr_disabled"),
    ]

    operations = [
        migrations.AlterField(
            model_name="document",
            name="public",
            field=models.BooleanField(
                default=False,
                help_text="Soll man dieses Dokument ohne Login downloaden können?",
                verbose_name="Öffentlich",
            ),
        ),
    ]
