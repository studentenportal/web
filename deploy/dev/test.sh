#!/bin/bash
#
# Pass in the --coverage-xml argument to generate XML coverage reports!

USAGE="$0 [--help] [--coverage-xml]"

# Parse arguments
while [[ "$#" -gt 0 ]]; do case $1 in
  --coverage-xml) generate_xml=1;;
  --help) echo "Usage: $USAGE"; exit 1;;
  *) echo "Unknown parameter passed: $1"; echo "Usage: $USAGE"; exit 1;;
esac; shift; done

# Wait for postgres
while ! curl "http://$POSTGRES_HOST:5432/" 2>&1 | grep '52' > /dev/null
do
  sleep 1
done

export PYTHONPATH=$(pwd)

PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d template1 -c 'CREATE EXTENSION IF NOT EXISTS citext;'
coverage run --source apps -m pytest "$@"
pytest_exit=$?

echo ""
(( pytest_exit == 0 )) && coverage report
if [[ "$generate_xml" == 1 ]]; then echo "Generating XML coverage file"; coverage xml; fi

exit "$pytest_exit"
