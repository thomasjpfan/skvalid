.PHONY: dev dev_conda package clean lint docs

lint:
	flake8 skvalid tests

dev:
	pip install -e .[dev]

dev_conda:
	conda env create -f requirements/conda.yml
	source activate skvalid_dev && \
	pip install -e .[dev]

release:
	python setup.py sdist
	python setup.py bdist_wheel

clean:
	rm -rf dist build */*.egg-info *.egg-info
	# $(MAKE) -C docs clean

docs:
	$(MAKE) -C docs html
