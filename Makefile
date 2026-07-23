.PHONY: install test validate-names generate placebo analyze power figures reproduce live clean

install:
	python -m pip install -e ".[dev]"

test:
	ruff check .
	pytest -q

validate-names:
	compas-validate-names --config config/audit.yaml

generate:
	compas-generate --config config/audit.yaml

placebo: generate
	compas-run --config config/audit.yaml --provider mock

analyze:
	compas-analyze --input outputs/screening_results.csv --output-dir outputs/analysis

power:
	python scripts/power_analysis.py

figures:
	python scripts/make_result_figures.py

reproduce:
	bash scripts/reproduce_all_results.sh

live:
	bash scripts/run_live_audit.sh

clean:
	rm -rf outputs/*.csv outputs/*.json outputs/analysis
