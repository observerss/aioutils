develop:
	python setup.py develop
publish:
	python setup.py sdist upload
test:
	PYTHONPATH=. nosetests -v --with-coverage --cover-package=aioutils tests/
