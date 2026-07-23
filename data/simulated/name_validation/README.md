# Simulated perception-study data

This directory contains a deterministic simulation used to test the name-validation pipeline.

It contains 120 simulated panel respondents rating all eight candidate names. Four simulated respondents fail the attention check, leaving 116 valid responses per name.

These files are not participant data and cannot be used as evidence that people perceive the names in the simulated way. They do not update `data/name_validation/perception_responses.csv`, do not change the repository's real-survey status, and cannot unlock a live Claude audit.

Generate the files with:

```bash
compas-simulate-name-pretest
```

Outputs are written under `results/simulated/name_validation/`.
