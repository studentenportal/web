# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from model_mommy import mommy
from model_mommy.recipe import Recipe

from apps.documents import models as document_models


documentcategory = Recipe(document_models.DocumentCategory,
    name='An1I',
    description='Analysis 1 für Informatiker',
)


def documentcategory_get_or_create():
    dc = document_models.DocumentCategory.objects.filter(name='An1I')
    if dc.exists():
        return dc.get()
    return mommy.make_recipe('apps.documents.documentcategory')

document_summary = Recipe(document_models.Document,
        dtype=document_models.Document.DTypes.SUMMARY,
        category=documentcategory_get_or_create)
document_exam = Recipe(document_models.Document,
        dtype=document_models.Document.DTypes.EXAM,
        category=documentcategory_get_or_create)
document_software = Recipe(document_models.Document,
        dtype=document_models.Document.DTypes.SOFTWARE,
        category=documentcategory_get_or_create)
document_learning_aid = Recipe(document_models.Document,
        dtype=document_models.Document.DTypes.LEARNING_AID,
        category=documentcategory_get_or_create)
