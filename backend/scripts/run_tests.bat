@echo off
echo Running pytest test suite with coverage...
python -m pytest backend/tests -v --cov=backend/app/etl --cov=backend/app/analysis --cov-report=term-missing
pause
