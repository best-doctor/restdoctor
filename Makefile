style:
	flake8 restdoctor
types:
	mypy --python-version 3.8 restdoctor
test:
	python -m pytest --cov=restdoctor --cov-report=xml -p no:warnings --disable-socket

check:
	make test style types

install-dev:
	pip-sync requirements.txt requirements-dev.txt

lock:
	pip-compile --generate-hashes
	pip-compile --generate-hashes requirements-dev.in
