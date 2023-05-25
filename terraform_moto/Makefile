# Makefile

install:
	pip3 install -r requirements.txt

lint-pylint:
	python3 -m pylint --disable=R,C,W0621,E1120 --recursive=y . --fail-under=8

lint-flake8:
	python3 -m flake8 --ignore=E501 --statistics

test:
	python3 -m pytest -vv tests/

init:
	terraform init

validate:
	terraform validate

deploy:
	terraform apply --auto-approve
