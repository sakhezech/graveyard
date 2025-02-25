build:
	./build

watch:
	./build -w 0.0.0.0:5000

check:
	ruff check .
	ruff format --check .
	npx prettier --check .

format:
	ruff check --fix .
	ruff format .
	npx prettier -w .

write:
	./write_post
	npx prettier -w ./pages/index.html

post:
	git add ./pages/index.html
	git commit
	git push

.PHONY: *
