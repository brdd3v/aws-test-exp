# Makefile

install:
	pip3 install -r requirements.txt

lint:
	cfn-lint -t resources.yml

test:
	python3 -m pytest -vv test_template_gen.py

taskcat-test:
	taskcat test run