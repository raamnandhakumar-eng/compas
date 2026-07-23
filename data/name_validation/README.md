# Name validation data

`name_candidates.csv` records the official Census and SSA source screen for each candidate name.

`perception_responses.csv` is an empty response template for the separate human perception pretest. Do not add invented or model-generated survey responses.

The current registry is intentionally marked pending. It should remain that way until the official source fields are completed and real survey responses have been collected.

Run `compas-validate-names --config config/audit.yaml` after the pretest is complete.
