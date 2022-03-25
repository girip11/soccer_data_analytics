#!/bin/bash
FILE=$1

echo "Running autoflake"
pipenv run autoflake -i --remove-all-unused-imports "$FILE"

echo "Running isort"
pipenv run isort "$FILE"

echo "Running pyupgrade"
pipenv run pyupgrade "$FILE"
