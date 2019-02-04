# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators
import apps.documents.models
import apps.front.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name='Titel')),
                ('description', models.CharField(help_text='(Max. 500 Zeichen)', max_length=500, verbose_name='Beschreibung', blank=True)),
                ('url', models.URLField(help_text='z.B. Link zu Github Repository', null=True, verbose_name='URL', blank=True)),
                ('dtype', models.PositiveSmallIntegerField(verbose_name='Typ', choices=[(1, 'Zusammenfassung'), (2, 'Pr\xfcfung'), (3, 'Software'), (4, 'Lernhilfe'), (5, 'Testat')])),
                ('document', models.FileField(help_text='(Max. 20MB)', upload_to=apps.documents.models.document_file_name, verbose_name='Datei')),
                ('original_filename', models.CharField(max_length=255, verbose_name='Originaler Dateiname', blank=True)),
                ('upload_date', models.DateTimeField(auto_now_add=True, verbose_name='Uploaddatum')),
                ('change_date', models.DateTimeField(verbose_name='Letztes \xc4nderungsdatum')),
                ('license', models.PositiveSmallIntegerField(blank=True, help_text='Lizenz, siehe <a href="http://creativecommons.org/choose/?lang=de">http://creativecommons.org/choose/?lang=de</a> um eine passende Lizenz auszuw\xe4hlen.<br>Empfohlen: CC BY-SA-NC 3.0', null=True, verbose_name='Lizenz', choices=[(1, 'Public Domain'), (2, 'CC BY 3.0'), (3, 'CC BY-SA 3.0'), (4, 'CC BY-NC 3.0'), (5, 'CC BY-NC-SA 3.0')])),
                ('public', models.BooleanField(default=True, help_text='Soll man dieses Dokument ohne Login downloaden k\xf6nnen?', verbose_name='\xd6ffentlich')),
                ('flattr_disabled', models.BooleanField(default=False, help_text='Soll Flattr f\xfcr dieses Dokument deaktiviert werden?', verbose_name='Flattr deaktivieren')),
            ],
            options={
                'ordering': ('-change_date',),
                'get_latest_by': 'change_date',
            },
        ),
        migrations.CreateModel(
            name='DocumentCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', apps.front.fields.CaseInsensitiveSlugField(help_text='z.B. "CompT1" oder "Prog3"', unique=True, max_length=32, verbose_name='K\xfcrzel')),
                ('description', models.CharField(help_text='z.B. "Computertechnik 1" oder "Programmieren 3"', max_length=255, verbose_name='Voller Name')),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'Modul',
            },
        ),
        migrations.CreateModel(
            name='DocumentDownload',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('ip', models.GenericIPAddressField(unpack_ipv4=True, editable=False, db_index=True)),
            ],
        ),
        migrations.CreateModel(
            name='DocumentRating',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('rating', models.PositiveSmallIntegerField(validators=[django.core.validators.MaxValueValidator(10), django.core.validators.MinValueValidator(1)])),
                ('document', models.ForeignKey(related_name='DocumentRating', to='documents.Document')),
            ],
        ),
    ]
