SHELL:=/usr/bin/env bash # Use bash syntax, mitigates dash's printf on Debian
export TOP:=$(shell dirname "$(abspath $(lastword $(MAKEFILE_LIST)))")
name:=$(shell basename "$(TOP)")
export PIP_FIND_LINKS:=$(abspath $(TOP)/whl_local/)
export PYTHONPATH:=$(TOP)/src


.PHONY: help
help:
	@echo
	@echo "▍Help"
	@echo "▀▀▀▀▀▀"
	@echo
	@echo "Available targets:"
	@echo "    check:              run checks"
	@echo "    test:               run all tests"
	@echo "    coverage:           run all tests and collect code coverage"
	@echo "    lint:               run linters"
	@echo
	@echo "    pep8format:         auto-format code to PEP8 standards"
	@echo
	@echo "    build:              build the source and whl package, look for */dist/*.whl"
	@echo
	@echo "    clean:              clean the build tree"
	@echo
	@echo "name='$(name)'"
	@echo "PYTHONPATH     = '$(PYTHONPATH)'"
	@echo "PIP_FIND_LINKS = '$(PIP_FIND_LINKS)'"


.PHONY: check
check: lint


.PHONY: test
test:
	pytest -v


.PHONY: coverage
coverage:
	pytest --cov=.


.PHONY: lint
lint:
	pylint "src/$(name)"


.PHONY: pep8format
pep8format:
	autopep8 --in-place --recursive "src/$(name)"


.PHONY: build
build:
	python3 -m build
	mkdir -p "$(PIP_FIND_LINKS)/"
	cp dist/*.whl "$(PIP_FIND_LINKS)/"


.PHONY: userinstall
userinstall: build
	python3 -m pip install $(PIP_USER) ./dist/*.whl


.PHONY: uninstall
uninstall:
	python3 -m pip uninstall -y "$(name)"


.PHONY: useruninstall
useruninstall: uninstall


.PHONY: rpmprep
rpmprep:
	cp "rpm/$(name).spec.in" "$(name).spec"
	sed -i 's|^Release:.*|Release:        $(RPM_REV)%{?dist}|g' "$(name).spec"
	sed -i 's|^Version:.*|Version:        $(RPM_VER)|g' "$(name).spec"
	rm -rf ~/rpmbuild/RPMS/noarch/"$(name)"*.rpm
	rm -rf ~/rpmbuild/SRPMS/"$(name)"*.src.rpm
	python3 setup.py sdist


.PHONY: rpm
rpm: rpmprep
	rpmbuild -ba "$(name).spec" --define "_sourcedir $$PWD/dist"
	rm "$(name).spec"


.PHONY: srpm
srpm: rpmprep
	rpmbuild -bs "$(name).spec" --define "_sourcedir $$PWD/dist"
	rm "$(name).spec"


.PHONY: clean
clean:
	-python3 -m coverage erase
	-python3 -m pip uninstall -y "$(name)"
	find . -depth \( -name '*.pyc' -o -name '__pycache__' -o -name '__pypackages__' \
		-o -name '*.pyc' -o -name '*.pyd' -o -name '*.pyo' -o -name '*.egg-info' \
		-o -name '*.py,cover'  \) -not -path "./.?*/*" \
		-exec rm -rf \{\} \;
	rm -rf site.py build/ dist/ "$(name).spec" VERSION bin/ .tox/ .pytest_cache/


# https://packaging.python.org/en/latest/guides/using-testpypi/
# Upload to https://test.pypi.org/
.PHONY: test_upload
test_upload: build
	twine upload --repository testpypi dist/keyclean-*.whl dist/keyclean-*.tar.gz


# Upload to https://pypi.org/
.PHONY: upload
upload: build
	twine upload dist/keyclean-*.whl dist/keyclean-*.tar.gz
