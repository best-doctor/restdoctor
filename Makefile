style:
	flake8 restdoctor
types:
	mypy --python-version 3.8 restdoctor
test:
	python -m pytest --cov=restdoctor --cov-report=xml -p no:warnings --disable-socket

check:
	make test style types

lock:
	pip-compile --generate-hashes
	pip-compile --generate-hashes requirements-dev.in
