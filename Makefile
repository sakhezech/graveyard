build:
	python -m pagebuilder -b builder:builder

watch:
	python -m pagebuilder -b builder:builder -w 0.0.0.0:5000

check:
	ruff check .
	ruff format --check .
	npx prettier . --check --ignore-path

format:
	ruff check --fix .
	ruff format .
	npx prettier . --ignore-path -w

.PHONY: *
