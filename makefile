NAME = fly_in.py
PYTHON = python
PIP = pip

.PHONY: install run debug clean lint lint-strict

install:
	$(PIP) install flake8 mypy

run:
	$(PYTHON) $(NAME) $(MAP)

debug:
	$(PYTHON) -m pdb $(NAME) $(MAP)

clean:
	$(PYTHON) -c "import shutil; shutil.rmtree('__pycache__', ignore_errors=True); shutil.rmtree('.mypy_cache', ignore_errors=True)"

lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 .
	mypy . --strict
