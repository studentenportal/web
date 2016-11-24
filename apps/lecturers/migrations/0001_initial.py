# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.IntegerField(serialize=False, verbose_name='Studiengang ID', primary_key=True)),
                ('abbreviation', models.CharField(unique=True, max_length=10, verbose_name='Abk\xfcrzung')),
                ('name', models.CharField(max_length=50, verbose_name='Titel')),
            ],
        ),
        migrations.CreateModel(
            name='Lecturer',
            fields=[
                ('id', models.IntegerField(serialize=False, verbose_name='HSR ID', primary_key=True)),
                ('title', models.CharField(max_length=32, null=True, verbose_name='Titel', blank=True)),
                ('last_name', models.CharField(max_length=255, verbose_name='Name')),
                ('first_name', models.CharField(max_length=255, verbose_name='Vorname')),
                ('abbreviation', models.CharField(unique=True, max_length=10, verbose_name='K\xfcrzel')),
                ('department', models.CharField(max_length=100, null=True, verbose_name='Abteilung', blank=True)),
                ('function', models.CharField(max_length=255, null=True, verbose_name='Funktion', blank=True)),
                ('main_area', models.CharField(max_length=255, null=True, verbose_name='Fachschwerpunkt', blank=True)),
                ('subjects', models.CharField(max_length=50, null=True, blank=True)),
                ('email', models.EmailField(max_length=254, null=True, blank=True)),
                ('office', models.CharField(max_length=20, null=True, blank=True)),
            ],
            options={
                'ordering': ['last_name'],
            },
        ),
        migrations.CreateModel(
            name='LecturerRating',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('category', models.CharField(db_index=True, max_length=1, choices=[('d', 'Didaktisch'), ('m', 'Menschlich'), ('f', 'Fachlich')])),
                ('rating', models.PositiveSmallIntegerField(db_index=True, validators=[django.core.validators.MaxValueValidator(10), django.core.validators.MinValueValidator(1)])),
                ('lecturer', models.ForeignKey(related_name='LecturerRating', to='lecturers.Lecturer')),
                ('user', models.ForeignKey(related_name='LecturerRating', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Quote',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('quote', models.TextField(verbose_name='Zitat')),
                ('comment', models.TextField(default='', verbose_name='Bemerkung', blank=True)),
                ('author', models.ForeignKey(related_name='Quote', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
                ('lecturer', models.ForeignKey(related_name='Quote', verbose_name='Dozent', to='lecturers.Lecturer')),
            ],
            options={
                'ordering': ['-date'],
                'get_latest_by': 'date',
            },
        ),
        migrations.CreateModel(
            name='QuoteVote',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('vote', models.BooleanField(help_text='True = upvote, False = downvote')),
                ('quote', models.ForeignKey(related_name='QuoteVote', to='lecturers.Quote')),
                ('user', models.ForeignKey(related_name='QuoteVote', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='quotevote',
            unique_together=set([('user', 'quote')]),
        ),
        migrations.AlterUniqueTogether(
            name='lecturerrating',
            unique_together=set([('user', 'lecturer', 'category')]),
        ),
    ]
