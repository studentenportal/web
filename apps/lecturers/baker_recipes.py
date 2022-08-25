from model_bakery.recipe import Recipe

from . import models

lecturer = Recipe(
    models.Lecturer,
    id=1337,
    title="Prof. Dr.",
    first_name="David",
    last_name="Krakaduku",
    abbreviation="KRA",
    email="kraka.duku@ost.ch",
    office="1.337",
    subjects="Quantenphysik, Mathematik für Mathematiker",
)
