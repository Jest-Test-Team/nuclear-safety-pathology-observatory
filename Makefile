PYTHON ?= python3

.PHONY: demo analyze test run-api run-web validate clean collect research oci-validate oci-plan oci-apply

demo:
	PYTHONPATH=services/pipeline $(PYTHON) scripts/generate_demo.py
	PYTHONPATH=services/pipeline $(PYTHON) -m nspo.engine.cli --input data/synthetic/observations.json --rules rules/patterns.yaml --output data/derived/findings.json

analyze:
	PYTHONPATH=services/pipeline $(PYTHON) -m nspo.engine.cli --input data/synthetic/observations.json --rules rules/patterns.yaml --output data/derived/findings.json

collect:
	PYTHONPATH=services/pipeline $(PYTHON) -m nspo.engine.collect --source $(SOURCE) $(if $(INPUT),--input-file $(INPUT),) $(if $(STATIONS),--station-file $(STATIONS),)

research:
	PYTHONPATH=services/pipeline $(PYTHON) -m nspo.engine.research_report

test:
	PYTHONPATH=services/pipeline $(PYTHON) -m pytest -q services/pipeline/tests
	cd apps/api && go test ./...
	PYTHONPATH=services/pipeline $(PYTHON) scripts/validate_repo.py

run-api:
	cd apps/api && NSPO_DATA_DIR=../../data/derived NSPO_REVIEW_STORE=../../data/runtime/reviews.json go run ./cmd/server

run-web:
	$(PYTHON) -m http.server 8081 -d apps/web

validate:
	PYTHONPATH=services/pipeline $(PYTHON) scripts/validate_repo.py

oci-validate:
	chmod +x scripts/oci/*.sh
	./scripts/oci/validate.sh

oci-plan:
	chmod +x scripts/oci/*.sh
	./scripts/oci/plan.sh

oci-apply:
	chmod +x scripts/oci/*.sh
	./scripts/oci/apply.sh

clean:
	rm -rf data/derived/* data/runtime .pytest_cache services/pipeline/**/__pycache__
