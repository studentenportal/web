# Generated by Django 3.1.4 on 2021-01-17 14:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("front", "0007_remove_user_flattr"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="first_name",
            field=models.CharField(
                blank=True, max_length=150, verbose_name="first name"
            ),
        ),
    ]
