PYTHON ?= python3
RSCRIPT ?= Rscript

.PHONY: setup environment manifest baseline independent-r-baseline test verify-code verify-preapproval verify-r-baseline multiverse cos-results

setup:
	$(PYTHON) -m pip install -r requirements-lock.txt
	$(PYTHON) -m pip install -e . --no-deps

environment:
	$(PYTHON) src/check_environment.py

manifest:
	$(PYTHON) src/write_manifest.py

baseline:
	$(PYTHON) src/run_registered_baseline.py

independent-r-baseline:
	$(PYTHON) src/run_independent_r_baseline.py --rscript $(RSCRIPT)

test:
	$(PYTHON) -m pytest --cov=odmk --cov=run_multiverse --cov-branch --cov-report=term-missing

verify-code: environment manifest test

verify-preapproval: verify-code baseline

verify-r-baseline: baseline independent-r-baseline

multiverse:
	$(PYTHON) src/run_multiverse.py --confirm-approved

cos-results:
	$(PYTHON) src/export_cos_results.py
