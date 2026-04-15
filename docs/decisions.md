# Decisions

This document is the canonical record of project choices.
Use it for official decisions that should guide the project going forward, such as data labeling standards, workflow definitions, and other agreed project conventions.

## 2026-04-15

- Project API credentials should be stored in `etc/` rather than embedded in code or general documentation.
- Credential-based local configuration should be initialized from tracked template files such as `etc/tokens.json.initial`, with real secrets stored only in local working copies such as `etc/tokens.json`.
- Synoptic metadata reference lists should be cached locally under `data/` when retrieved so downstream data-building and model-training steps do not depend on repeated live API access.
- Canonical first-stage local copies of Synoptic metadata should be saved as raw API JSON before any flattening or CSV conversion.
- Live Synoptic retrieval is an explicit token-using step and should be treated as a confirmed action, with the token stored only in untracked local config such as `etc/tokens.json`.
