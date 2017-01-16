#!/bin/bash

export TWITTER_CONSUMER_KEY=bHCF7StTA5E6qpbkNdOAA
export TWITTER_CONSUMER_SECRET=dqZg18xISSXfqHXKCuDnlj83DcH8OfrO1vO8kCT2sus
export TWITTER_ACCESS_KEY=505685594-GT9JYo0DQYTowjiFpviX0iGtqTc5qxkgtvoFT5pV
export TWITTER_ACCESS_SECRET=ORiGqX32m8KoSGTW8kSWz9CeW3YU3BbvUfbkXc51J700t

PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER  -d template1 -c 'CREATE EXTENSION IF NOT EXISTS citext;'
coverage run --source apps -m py.test \
&& echo \
&& coverage report
