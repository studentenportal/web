#!/bin/bash
coverage run --source apps -m py.test \
&& echo \
&& coverage report
