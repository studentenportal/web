# Generated by Django 2.2.9 on 2020-01-21 16:25

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("front", "0003_username_normalization"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="last_name",
            field=models.CharField(
                blank=True, max_length=150, verbose_name="last name"
            ),
        ),
    ]
