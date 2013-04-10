#!/bin/bash
coverage run manage.py test $1 \
&& echo \
&& coverage report
