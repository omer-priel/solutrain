@ECHO OFF

REM This script runs all the linters of backend

cd ../backend
python -m flake8 src
python -m black --check --diff src
python -m mypy src