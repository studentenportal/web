#!/bin/bash
coverage run manage.py test $1 \
&& echo \
&& coverage report --include="./*" --omit="manage.py,admin.py,*/migrations/*,*/tests/*"
