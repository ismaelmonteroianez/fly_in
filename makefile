NAME = fly_in.py
PYTHON = python3
PIP = $(PYTHON) -m pip

.PHONY: install run debug clean lint lint-strict

install:
	$(PIP) install flake8 mypy

run:
	$(PYTHON) $(NAME) $(MAP)

debug:
	$(PYTHON) -m pdb $(NAME) $(MAP)

clean:
	rm -rf __pycache__/
	rm -rf .mypy_cache/
	rm -rf .pytest_cache/

lint:
	$(PYTHON) -m flake8 .
	$(PYTHON) -m mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	$(PYTHON) -m flake8 .
	$(PYTHON) -m mypy . --strict
