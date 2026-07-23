.PHONY: install test validate-names simulate-name-pretest generate placebo analyze \
	power figures reproduce live core-generate core-placebo core-analyze \
	core-reproduce core-live select-balanced-names clean

install:
	python -m pip install -e ".[dev]"

test:
	ruff check .
	pytest -q

validate-names:
	compas-validate-names --config config/audit.yaml

simulate-name-pretest:
	compas-simulate-name-pretest --config config/audit.yaml

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

core-generate:
	compas-generate --config config/core_audit.yaml

core-placebo: core-generate
	compas-run --config config/core_audit.yaml --provider mock

core-analyze:
	compas-analyze-core \
		--input outputs/core/screening_results.csv \
		--output-dir outputs/core/analysis

core-reproduce:
	bash scripts/reproduce_core_placebo.sh

core-live:
	bash scripts/run_core_live_audit.sh

select-balanced-names:
	compas-select-balanced-names \
		--input results/name_validation/replacement_candidate_summary.csv

clean:
	rm -rf outputs/*.csv outputs/*.json outputs/analysis outputs/core
