# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from django.contrib.auth import get_user_model

from model_mommy import mommy
from model_mommy.recipe import Recipe, foreign_key

from apps.front import models


lecturer = Recipe(models.Lecturer,
    # TODO report negative PKs
    id=1337,
    title='Prof. Dr.',
    first_name='David',
    last_name='Krakaduku',
    abbreviation='KRA',
    email='krakaduku@hsr.ch',
    office='1.337',
    subjects='Quantenphysik, Mathematik für Mathematiker',
)


User = get_user_model()
user = Recipe(User,
    username='testuser',
    password='sha1$4b2d5$c6ff8b2ff002131f58cfb0a5b43a6681a0b723b3',
    email='test@studentenportal.ch',
)


documentcategory = Recipe(models.DocumentCategory,
    name='An1I',
    description='Analysis 1 für Informatiker',
)


def documentcategory_get_or_create():
    dc = models.DocumentCategory.objects.filter(name='An1I')
    if dc.exists():
        return dc.get()
    return mommy.make_recipe('apps.front.documentcategory')

document_summary = Recipe(models.Document,
        dtype=models.Document.DTypes.SUMMARY,
        category=documentcategory_get_or_create)
document_exam = Recipe(models.Document,
        dtype=models.Document.DTypes.EXAM,
        category=documentcategory_get_or_create)
document_software = Recipe(models.Document,
        dtype=models.Document.DTypes.SOFTWARE,
        category=documentcategory_get_or_create)
document_learning_aid = Recipe(models.Document,
        dtype=models.Document.DTypes.LEARNING_AID,
        category=documentcategory_get_or_create)
