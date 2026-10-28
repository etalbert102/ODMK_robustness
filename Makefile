PYTHON ?= python3

.PHONY: setup environment manifest baseline test verify-code verify-preapproval multiverse

setup:
	$(PYTHON) -m pip install -r requirements-lock.txt
	$(PYTHON) -m pip install -e . --no-deps

environment:
	$(PYTHON) src/check_environment.py

manifest:
	$(PYTHON) src/write_manifest.py

baseline:
	$(PYTHON) src/run_registered_baseline.py

test:
	$(PYTHON) -m pytest

verify-code: environment manifest test

verify-preapproval: verify-code baseline

multiverse:
	$(PYTHON) src/run_multiverse.py --confirm-approved
