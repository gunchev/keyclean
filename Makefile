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
	@echo "    release:            tag a new release (required: V=X.Y.Z)"
	@echo "                        updates version in pyproject.toml + __init__.py,"
	@echo "                        prepends git log to CHANGELOG.md, commits, tags."
	@echo "                        Example: make V=0.2.0 release"
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


# Python script that prepends a new section to CHANGELOG.md.
# Exported as an env var so the recipe can pipe it to python3 via stdin
# without heredoc/quoting nightmares.
define _release_py
import subprocess, datetime, pathlib, sys
v, top = sys.argv[1], sys.argv[2]
cl = pathlib.Path(top, "CHANGELOG.md")
tags = subprocess.check_output(
    ["git", "-C", top, "tag", "--sort=-version:refname"],
    text=True
).strip().splitlines()
tags = [t for t in tags if t]
last_tag = tags[0] if tags else None
log_range = [last_tag + "..HEAD"] if last_tag else []
commits = subprocess.check_output(
    ["git", "-C", top, "log"] + log_range +
    ["--oneline", "--no-decorate", "--no-merges"],
    text=True
).strip()
date = datetime.date.today().isoformat()
since = last_tag if last_tag else "beginning"
section = "## " + v + " \u2014 " + date + "\n\n"
section += "### Changes since " + since + "\n\n"
if commits:
    section += "\n".join("- " + c for c in commits.splitlines()) + "\n"
section += "\n"
existing = cl.read_text()
cl.write_text(section + existing)
n = len(commits.splitlines()) if commits else 0
print("Updated CHANGELOG.md (" + str(n) + " commit" + ("s" if n != 1 else "") + ")")
endef
export _release_py


.PHONY: release
release:
	@[ -n "$(V)" ] || { echo "Error: V is not set.  Usage: make V=X.Y.Z release"; exit 1; }
	@printf '%s' "$(V)" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+$$' || \
		{ echo "Error: '$(V)' is not a valid version (expected X.Y.Z)"; exit 1; }
	@git -C "$(TOP)" diff --quiet HEAD 2>/dev/null || \
		{ echo "Error: uncommitted changes — commit or stash first"; exit 1; }
	@git -C "$(TOP)" tag | grep -qxF "v$(V)" && \
		{ echo "Error: tag v$(V) already exists"; exit 1; } || true
	@echo "▶ Bumping version to $(V) ..."
	sed -i 's/^version = ".*"/version = "$(V)"/' "$(TOP)/pyproject.toml"
	sed -i 's/^__version__ = ".*"/__version__ = "$(V)"/' \
		"$(TOP)/src/$(name)/__init__.py"
	@echo "▶ Updating CHANGELOG.md ..."
	printf '%s\n' "$$_release_py" | python3 - "$(V)" "$(TOP)"
	@echo "▶ Committing and tagging v$(V) ..."
	git -C "$(TOP)" add pyproject.toml "src/$(name)/__init__.py" CHANGELOG.md
	git -C "$(TOP)" commit -m "Release $(V)"
	git -C "$(TOP)" tag -a "v$(V)" -m "Version $(V)"
	@echo
	@echo "✓ Released v$(V).  Push with:"
	@echo "      git push && git push --tags"


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
