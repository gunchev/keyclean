SHELL:=/usr/bin/env bash # Use bash syntax, mitigates dash's printf on Debian
export TOP:=$(shell dirname "$(abspath $(lastword $(MAKEFILE_LIST)))")
name:=$(shell basename "$(TOP)")
_UNAME:=$(shell uname -s 2>/dev/null)
ifeq ($(_UNAME),Linux)
  _OS_EXTRA:=--extra linux
else ifeq ($(_UNAME),Darwin)
  _OS_EXTRA:=--extra macos
else
  _OS_EXTRA:=--extra windows
endif
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
	@echo "    release:            tag a new release (required: V=X.Y.Z), e.g. make V=1.0.0 release"
	@echo
	@echo "    run:                sync dev environment and run the app (development mode)"
	@echo
	@echo "    clean:              clean the build tree"
	@echo
	@printf "Makefile debug: name=%q, PYTHONPATH=%q, PIP_FIND_LINKS=%q\n\n" "$(name)" "$(PYTHONPATH)" "$(PIP_FIND_LINKS)"


.PHONY: check
check: lint


.PHONY: test
test:
	pytest -v


.PHONY: coverage
coverage:
	pytest -v --cov . --cov-report=term-missing


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


.PHONY: run
run:
	uv sync --group dev $(_OS_EXTRA) --extra grab
	uv run keyclean


.PHONY: release
release:
	@[ -n "$(V)" ] || { echo "Error: V is not set.  Usage: make V=X.Y.Z release"; exit 1; }
	"$(TOP)/release.py" "$(V)"


.PHONY: clean
clean:
	-python3 -m coverage erase
	find "$(TOP)" -depth \( -name '__pycache__' -o -name '*.pyc' -o -name '*.pyo' -o -name '*.pyd' -o -name '*.egg-info' -o -name '*.py,cover' \) \
		-not -path '*/.git/*' -exec rm -rf {} +
	rm -rf "$(TOP)/build/" "$(TOP)/dist/" "$(TOP)/.tox/" \
		"$(TOP)/.pytest_cache/" "$(TOP)/.coverage"


# https://packaging.python.org/en/latest/guides/using-testpypi/
# Upload to https://test.pypi.org/
# release.py builds the distribution at the tagged commit before bumping
# to the next dev version, so upload must NOT rebuild (that would pick up
# the -dev __version__).  Just run twine on whatever release.py left in dist/.
.PHONY: test_upload
test_upload:
	twine upload --repository testpypi dist/keyclean-*.whl dist/keyclean-*.tar.gz


# Upload to https://pypi.org/
.PHONY: upload
upload:
	twine upload dist/keyclean-*.whl dist/keyclean-*.tar.gz
