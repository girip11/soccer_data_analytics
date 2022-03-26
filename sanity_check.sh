#!/bin/bash

set -eu

echo "Running black"
python -m black -t py38 -l 100 --check src tests
echo "Running isort"
python -m isort --py 38 --check src tests
echo "Running flake8"
python -m flake8 src tests
echo "Running mypy"
python -m mypy src tests
echo "Running pytest"
python -m pytest tests
