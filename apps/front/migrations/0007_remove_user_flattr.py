# Generated by Django 2.2.11 on 2020-03-12 11:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('front', '0006_change_user_manager'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='flattr',
        ),
    ]