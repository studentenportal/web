# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import, unicode_literals

from model_bakery import baker
from model_bakery.recipe import Recipe

from apps.documents import models as document_models


documentcategory = Recipe(
    document_models.DocumentCategory,
    name="An1I",
    description="Analysis 1 für Informatiker",
)


def documentcategory_get_or_create():
    dc = document_models.DocumentCategory.objects.filter(name="An1I")
    if dc.exists():
        return dc.get()
    return baker.make_recipe("apps.documents.documentcategory")


document_summary = Recipe(
    document_models.Document,
    dtype=document_models.Document.DTypes.SUMMARY,
    category=documentcategory_get_or_create,
    _create_files=True,
)
document_exam = Recipe(
    document_models.Document,
    dtype=document_models.Document.DTypes.EXAM,
    category=documentcategory_get_or_create,
    _create_files=True,
)
document_software = Recipe(
    document_models.Document,
    dtype=document_models.Document.DTypes.SOFTWARE,
    category=documentcategory_get_or_create,
    _create_files=True,
)
document_learning_aid = Recipe(
    document_models.Document,
    dtype=document_models.Document.DTypes.LEARNING_AID,
    category=documentcategory_get_or_create,
    _create_files=True,
)
