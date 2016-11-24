# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import apps.events.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('summary', models.CharField(max_length=64, verbose_name='Titel')),
                ('description', models.TextField(verbose_name='Beschreibung')),
                ('start_date', models.DateField(help_text='Format: dd.mm.YYYY', verbose_name='Startdatum')),
                ('start_time', models.TimeField(help_text='Format: hh:mm', null=True, verbose_name='Startzeit', blank=True)),
                ('end_date', models.DateField(help_text='Format: dd.mm.YYYY', null=True, verbose_name='Enddatum', blank=True)),
                ('end_time', models.TimeField(help_text='Format: hh:mm', null=True, verbose_name='Endzeit', blank=True)),
                ('location', models.CharField(help_text='Veranstaltungsort, zB "Geb\xe4ude 3" oder "B\xe4ren Rapperswil"', max_length=80, null=True, verbose_name='Ort', blank=True)),
                ('url', models.URLField(help_text='URL zu Veranstaltungs-Website', null=True, verbose_name='URL', blank=True)),
                ('picture', models.ImageField(help_text='Bild oder Flyer', upload_to=apps.events.models.picture_file_name, null=True, verbose_name='Bild/Flyer', blank=True)),
            ],
        ),
    ]
