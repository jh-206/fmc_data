# Notes

This document is a running project log.
Use it for more detailed working notes, including what we tried, what happened, what failed, and what still needs follow-up.

## 2026-04-15

- Created [docs/data_sources.md](/Users/hirschij/Documents/Projects/Wildfire/fmc_data/docs/data_sources.md) as a stable reference document for important external project data and software sources.
- Added an initial set of authoritative URLs for:
  - Synoptic Weather API documentation
  - SynopticPy documentation
  - SynopticPy GitHub repository
  - NIFC RAWS home page
  - NIFC overview of Remote Automatic Weather Stations
- Deferred fuel sensor links for a later pass.
- Added Synoptic Variables, Networks, and Mesonet dataset overview documentation links to [docs/data_sources.md](/Users/hirschij/Documents/Projects/Wildfire/fmc_data/docs/data_sources.md).
- Created `etc/` as a local configuration directory for API credentials and related setup files.
- Added [etc/tokens.json.initial](/Users/hirschij/Documents/Projects/Wildfire/fmc_data/etc/tokens.json.initial) with a placeholder value for the Synoptic API token.
- Updated [README.md](/Users/hirschij/Documents/Projects/Wildfire/fmc_data/README.md) with setup notes describing how to obtain a Synoptic token and populate `etc/tokens.json`.
- Created a local untracked [etc/tokens.json](/Users/hirschij/Documents/Projects/Wildfire/fmc_data/etc/tokens.json) and updated [.gitignore](/Users/hirschij/Documents/Projects/Wildfire/fmc_data/.gitignore) so the live Synoptic token is not tracked.
- Attempted to retrieve Synoptic metadata from the `variables` and `networks` API endpoints using the local token.
- Initial API attempt failed inside the sandbox due to network resolution restrictions.
- Retried the same request with network access enabled and successfully saved local copies to:
  - [data/synoptic_variables.json](/Users/hirschij/Documents/Projects/Wildfire/fmc_data/data/synoptic_variables.json)
  - [data/synoptic_networks.json](/Users/hirschij/Documents/Projects/Wildfire/fmc_data/data/synoptic_networks.json)
- Retrieved counts from the saved payloads:
  - 265 entries in `VARIABLES`
  - 402 entries in `MNET`
- Investigated the origin of [archived/RAWSList_WXx.xlsx](/Users/hirschij/Documents/Projects/Wildfire/fmc_data/archived/RAWSList_WXx.xlsx) and found that it appears to match the NIFC WXx Weather station-search/export workflow.
- The likely upstream source is the WXx Weather point-and-click interface at [weather.nifc.gov](https://weather.nifc.gov/), but the exact export path was not reproducible agentically from the public interface because of validation/bot-protection barriers.
- For now, copied the prior manual export into [data/RAWSList_WXx.xlsx](/Users/hirschij/Documents/Projects/Wildfire/fmc_data/data/RAWSList_WXx.xlsx) as a temporary working data source for station and sensor metadata.
- Reviewed `synopticpy` installation and token-configuration behavior for local wrapper development.
- Added [etc/environment.yml](/Users/hirschij/Documents/Projects/Wildfire/fmc_data/etc/environment.yml) as a minimal Conda environment spec for Synoptic data-access and data-processing work.
- Chose `fmc_synoptic` as the local Conda environment name for this phase of the project.
- Created the local `fmc_synoptic` environment and verified `synopticpy==2024.12.0` is available there.
- Kept this environment intentionally narrow and data-processing focused rather than reproducing the broader package set from `ml_fmda_data`.
- Confirmed that `synopticpy` can use a token passed directly, the `SYNOPTIC_TOKEN` environment variable, or `~/.config/SynopticPy/config.toml`.
- Deferred local token initialization pending explicit confirmation because it requires using the live secret from [etc/tokens.json](/Users/hirschij/Documents/Projects/Wildfire/fmc_data/etc/tokens.json).
