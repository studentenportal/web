#!/bin/bash
coverage run --source=apps,backends manage.py test $1 \
&& echo \
&& coverage report --include="./*" --omit="manage.py,admin.py,*/migrations/*,*/tests/*"
