# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import os
import re
from datetime import datetime

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.functions import Coalesce, Round

from apps.lecturers import managers


def lecturer_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/lecturers/<filename>
    return f"lecturers/{filename}"


class Lecturer(models.Model):
    """A lecturer at HSR.

    If there is a photo of that lecturer, it should go into the media folder
    and the filename should be <abbreviation>.jpg.

    """

    id = models.AutoField("ID", primary_key=True)
    title = models.CharField("Titel", max_length=32, null=True, blank=True)
    last_name = models.CharField("Name", max_length=255)
    first_name = models.CharField("Vorname", max_length=255)
    abbreviation = models.CharField("Kürzel", max_length=10, unique=True)
    department = models.CharField("Abteilung", max_length=100, null=True, blank=True)
    function = models.CharField("Funktion", max_length=255, null=True, blank=True)
    main_area = models.CharField(
        "Fachschwerpunkt", max_length=255, null=True, blank=True
    )
    subjects = models.CharField(
        max_length=50, null=True, blank=True
    )  # todo add to frontend
    email = models.EmailField(null=True, blank=True)
    office = models.CharField(max_length=20, null=True, blank=True)
    picture = models.ImageField(
        "Bild",
        upload_to=lecturer_directory_path,
        null=True,
        blank=True,
    )

    objects = models.Manager()
    real_objects = managers.RealLecturerManager()

    def name(self):
        parts = [self.title, self.last_name, self.first_name]
        return " ".join(p for p in parts if p)

    def photo(self):
        """Try to see if a photo with the name <self.id>.jpg exists. If it
        does, return the corresponding URL. If it doesn't, return None."""
        if self.picture:
            path = self.picture.name
        else:
            path = os.path.join("lecturers", f"{self.id}.jpg")
        full_path = os.path.join(settings.MEDIA_ROOT, path)
        return path if os.path.exists(full_path) else None

    def oldphotos(self):
        """Try to see whether there are more pictures in the folder
        ``lecturers/old/<self.id>/``..."""
        path = os.path.join("lecturers", "old", str(self.id))
        fullpath = os.path.join(settings.MEDIA_ROOT, path)
        oldphotos = []
        if os.path.exists(fullpath):
            for filename in os.listdir(fullpath):
                if re.match(r"^[0-9]+\.jpg$", filename):
                    filepath = os.path.join(path, filename)
                    oldphotos.append(filepath)
        return oldphotos

    def _avg_rating(self, category):
        """Calculate the average rating for the given category."""
        return (
            self.LecturerRating.filter(category=category)
            .aggregate(avg=Coalesce(Round(models.Avg("rating")), models.Value(0)))
            .get("avg", 0)
        )

    def _rating_count(self, category):
        return self.LecturerRating.filter(category=category).count()

    def avg_rating_d(self):
        return self._avg_rating("d")

    def avg_rating_m(self):
        return self._avg_rating("m")

    def avg_rating_f(self):
        return self._avg_rating("f")

    def rating_count_d(self):
        return self._rating_count("d")

    def rating_count_m(self):
        return self._rating_count("m")

    def rating_count_f(self):
        return self._rating_count("f")

    def __str__(self):
        return "{} {}".format(self.last_name, self.first_name)

    class Meta:
        ordering = ["last_name"]


class LecturerRating(models.Model):
    """A lecturer rating. Max 1 per user, category and lecturer."""

    CATEGORY_CHOICES = (("d", "Didaktisch"), ("m", "Menschlich"), ("f", "Fachlich"))
    RATING_VALIDATORS = [MaxValueValidator(10), MinValueValidator(1)]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="LecturerRating",
        null=True,
        on_delete=models.SET_NULL,
    )
    lecturer = models.ForeignKey(
        Lecturer, related_name="LecturerRating", on_delete=models.CASCADE
    )
    category = models.CharField(max_length=1, choices=CATEGORY_CHOICES, db_index=True)
    rating = models.PositiveSmallIntegerField(
        validators=RATING_VALIDATORS, db_index=True
    )

    def __str__(self):
        return "%s %s%u" % (self.lecturer, self.category, self.rating)

    class Meta:
        unique_together = ("user", "lecturer", "category")


class Quote(models.Model):
    """Lecturer quotes."""

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="Quote",
        null=True,
        on_delete=models.SET_NULL,
    )
    lecturer = models.ForeignKey(
        Lecturer, verbose_name="Dozent", related_name="Quote", on_delete=models.CASCADE
    )
    date = models.DateTimeField(auto_now_add=True)
    quote = models.TextField("Zitat")
    comment = models.TextField("Bemerkung", default="", blank=True)

    def date_available(self):
        return self.date != datetime(1970, 1, 1)

    def vote_sum(self):
        """Add up and return all votes for this quote."""
        up = self.QuoteVote.filter(vote=True).count()
        down = self.QuoteVote.filter(vote=False).count()
        return up - down

    def __str__(self):
        return "[{}] {}...".format(self.lecturer, self.quote[:30])

    class Meta:
        ordering = ["-date"]
        get_latest_by = "date"


class QuoteVote(models.Model):
    """Lecturer quote votes."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="QuoteVote",
        null=True,
        on_delete=models.SET_NULL,
    )
    quote = models.ForeignKey(Quote, related_name="QuoteVote", on_delete=models.CASCADE)
    vote = models.BooleanField(help_text="True = upvote, False = downvote")

    def __str__(self):
        fmt_args = self.user.username, "up" if self.vote else "down", self.quote.pk
        return "User %s votes %s quote %s" % fmt_args

    class Meta:
        unique_together = ("user", "quote")


class Course(models.Model):
    """A possible degree course. At the moment only one lecturer is possible."""

    id = models.IntegerField("Studiengang ID", primary_key=True)
    abbreviation = models.CharField("Abkürzung", max_length=10, unique=True)
    name = models.CharField("Titel", max_length=50)

    def __str__(self):
        return "{} ({})".format(self.name, self.abbreviation)
