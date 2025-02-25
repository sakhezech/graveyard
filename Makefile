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

write:
	python write_post.py
	npx prettier ./pages/index.html -w

post:
	git add ./pages/index.html
	git commit
	git push

.PHONY: *
