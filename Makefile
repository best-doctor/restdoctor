style:
	flake8 restdoctor
types:
	mypy restdoctor
test:
	python -m pytest -p no:warnings --disable-socket
coverage:
	python -m pytest --cov=restdoctor --cov-report=xml -p no:warnings --disable-socket
check:
	make test style types

install-dev:
	pip-sync requirements.txt requirements-dev.txt

lock:
	pip-compile --generate-hashes --no-emit-index-url
	pip-compile --generate-hashes --no-emit-index-url requirements-dev.in
