.PHONY: backup

init:
	pipenv install --dev
	pipenv run githooks

test:
	pipenv run pytest

lint:
	pipenv run pylama
	pipenv run black ./qualitychecker ./tests --check --line-length 79

prettify:
	pipenv run black ./qualitychecker ./tests --line-length 79

pre-commit: lint test
