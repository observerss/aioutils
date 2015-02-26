publish:
	python setup.py sdist upload
develop:
	python setup.py develop
test:
	PYTHONPATH=. nosetests -v --with-coverage --cover-package=aioutils tests/
