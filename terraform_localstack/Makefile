# Makefile

install:
	pip3 install -r requirements.txt

init:
	terraform init

validate:
	terraform validate

run-localstack:
	docker pull localstack/localstack
	localstack start -d
	echo "Waiting for LocalStack startup..."
	localstack wait -t 30
	echo "Startup complete"

deploy-local:
	tflocal apply --auto-approve

lint-pylint:
	python3 -m pylint --disable=R,C,W0621 --recursive=y . --fail-under=8

lint-flake8:
	python3 -m flake8 --ignore=E501 --statistics

deploy:
	terraform apply --auto-approve
