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
