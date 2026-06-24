# Decisions

This document is the canonical record of project choices.
Use it for official decisions that should guide the project going forward, such as data labeling standards, workflow definitions, and other agreed project conventions.

## 2026-04-15

- Project API credentials should be stored in `etc/` rather than embedded in code or general documentation.
- Credential-based local configuration should be initialized from tracked template files such as `etc/tokens.json.initial`, with real secrets stored only in local working copies such as `etc/tokens.json`.
- Synoptic metadata reference lists should be cached locally under `data/` when retrieved so downstream data-building and model-training steps do not depend on repeated live API access.
- Canonical first-stage local copies of Synoptic metadata should be saved as raw API JSON before any flattening or CSV conversion.
- Live Synoptic retrieval is an explicit token-using step and should be treated as a confirmed action, with the token stored only in untracked local config such as `etc/tokens.json`.
- The project should maintain separate Python environments for distinct workflow layers when that improves stability and clarity.
- Synoptic API access and wrapper-building work should use a dedicated data-processing environment rather than sharing an environment with future modeling code.
- The initial dedicated data-processing environment is defined in [etc/environment.yml](/Users/hirschij/Documents/Projects/Wildfire/fmc_data/etc/environment.yml) and uses the Conda environment name `fmc_synoptic`.
- Synoptic-derived datasets stored under `data/` should include a companion build document that records the exact commands used to recreate them.
- Station inventory datasets built from Synoptic metadata should include any required request options needed to expose the intended sensor metadata, such as `sensorvars=1` for fuel moisture.
- Automated verification code should live in a top-level `tests/` directory rather than being mixed into `src/`.
- Data-access code and dataset-build workflows should remain token-agnostic and should not hard-code assumptions tied to a specific Synoptic account tier.
- The project’s intended full-scale historical data build for classifier development is expected to run with a paid Synoptic token so the training dataset can cover the broadest practical period of record available to the project.

## 2026-05-07

- Synoptic FMC ingest runs should use GACC bounding boxes as the primary spatial partitioning scheme, aligning project data retrieval with the regional structure already used in WRF-SFIRE workflows.

## 2026-05-10

- The historical FMC data stash maintained by the Wildfire Interdisciplinary Research Center (WIRC) will be used as the initial training source for the FMC sensor-validity classifier.
- Angel Farguell-Caus is the project contact for the WIRC historical FMC stash.
- Existing Synoptic API retrieval code will be used to test real-time classification on newly retrieved FMC observations.

## 2026-05-12

- Manually labeled FMC validity datasets stored under [data/labeled](/Users/hirschij/Documents/Projects/Wildfire/fmc_data/data/labeled:1) are the project training labels for valid and invalid fuel-moisture sensor periods.
- These manual valid/invalid labels should be used to train the initial FMC sensor-validity classifier.

## 2026-05-19

- Historical HRRR weather-model data stored under [data/hrrr_stash](/Users/hirschij/Documents/Projects/Wildfire/fmc_data/data/hrrr_stash:1) will be used as the initial historical weather-context source for training the FMC sensor-validity classifier.
- HRRR-derived weather features should be treated as source-aware model inputs, not assumed to be identical to future co-located Synoptic station weather observations.

## 2026-06-03

- Initial FMC sensor-validity model evaluation should use leave-one-GACC-out cross-validation, holding out one usable GACC at a time as the test set.
- Within each leave-one-GACC-out fold, training and validation splits should be station-grouped so all observations from a station remain in only one split.
- Dataset builds and model runs should support repeated random seeds to estimate variability from train/validation sampling and model-training stochasticity.
- Evaluation summaries should distinguish seed-replication variability from regional generalization variability across held-out GACCs.

## 2026-06-24

- The FMC sensor-validity classifier should be framed within the broader anomaly-detection literature, with the closest applied subfields being sensor fault detection, automated sensor-observation quality control, and sensor data validation.
- The initial project approach should remain supervised valid/invalid classification from manually labeled FMC validity intervals, rather than relying only on hand-written QC rules or purely unsupervised anomaly detection.
- Literature review and model-development work should prioritize time-series-based approaches because FMC sensor validity often depends on temporal structure rather than an isolated hourly value.
- Real-time classifier development should prioritize methods that use current and prior observations, while methods that require future observations should be treated as delayed or retrospective QC approaches.
- Initial model-development work should prioritize a small ML-focused comparison set: a simple supervised baseline with engineered temporal-window features, an RNN/LSTM sequence classifier, and a Transformer or attention-based sequence classifier.
- Model outputs should support threshold-based valid/invalid classification so operating points can be selected based on the relative costs of false valid and false invalid flags.
- Broader statistical QC methods may be cited as relevant background, but they are not the primary implementation focus for the initial classifier comparison.
- Initial sequence-model development should consider fixed lookback windows of 24, 48, and 72 hours as candidate temporal contexts.
- Initial training should use fixed, assumed-independent windows rather than long stateful station histories, as a simplifying choice for robust training over irregular real-world sensor records.
- RNN/LSTM validation and test workflows may use streaming prediction with carried recurrent state to evaluate the intended efficient real-time inference procedure.
- Stateful long-history training is not the current primary approach because outages, invalid periods, maintenance gaps, and other discontinuities make hidden-state management too cumbersome for the initial classifier workflow.
