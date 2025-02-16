build:
	python -m pagebuilder -b builder:builder

watch:
	python -m pagebuilder -b builder:builder -w 0.0.0.0:5000

.PHONY: *
