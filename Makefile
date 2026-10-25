PYTHON ?= python3

.PHONY: setup environment manifest baseline preflight test verify-preapproval multiverse

setup:
	$(PYTHON) -m pip install -r requirements-lock.txt
	$(PYTHON) -m pip install -e . --no-deps

environment:
	$(PYTHON) src/check_environment.py

manifest:
	$(PYTHON) src/write_manifest.py

baseline:
	$(PYTHON) src/baseline_analysis.py
	$(PYTHON) src/run_registered_baseline.py

preflight:
	$(PYTHON) src/preflight_registry.py

test:
	$(PYTHON) -m pytest

verify-preapproval: environment manifest test baseline preflight

multiverse:
	$(PYTHON) src/run_multiverse.py --confirm-approved
