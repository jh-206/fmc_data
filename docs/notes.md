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
- Added a top-level `tests/` directory for automated verification code rather than mixing tests into `src/`.
- Added [tests/test_synoptic_fuel_moisture.py](/Users/hirschij/Documents/Projects/Wildfire/fmc_data/tests/test_synoptic_fuel_moisture.py) as an initial Synoptic fuel-moisture access test script.
- Queried the Synoptic station metadata endpoint for stations matching `vars=fuel_moisture`.
- Found that `sensorvars=1` is required in the station metadata request if the returned payload should explicitly include `fuel_moisture` under `SENSOR_VARIABLES`.
- Saved the resulting station inventory to:
  - [data/synoptic_stations_fuel_moisture.json](/Users/hirschij/Documents/Projects/Wildfire/fmc_data/data/synoptic_stations_fuel_moisture.json)
  - [data/synoptic_stations_fuel_moisture.csv](/Users/hirschij/Documents/Projects/Wildfire/fmc_data/data/synoptic_stations_fuel_moisture.csv)
- Retrieved counts from the saved fuel-moisture station payload:
  - 4047 stations returned by the metadata request
  - 4047 stations with explicit `fuel_moisture` sensor metadata when `sensorvars=1` is included
- Added [data/DATASET_BUILD.md](/Users/hirschij/Documents/Projects/Wildfire/fmc_data/data/DATASET_BUILD.md) to document exact recreation commands for the current Synoptic-derived datasets in `data/`.
- Live-retested the documented build commands in `data/DATASET_BUILD.md` against the current token and confirmed they successfully rebuilt:
  - `synoptic_variables` outputs
  - `synoptic_networks` outputs
  - `synoptic_stations_fuel_moisture` outputs

## 2026-04-16

- Reviewed the installed `synopticpy` code path and found that it primarily wraps direct Synoptic API requests with token lookup, parameter normalization, and optional parsing to Polars DataFrames.
- Working hypothesis for follow-up exploration: canonical project dataset builds may be better implemented with direct API requests rather than `synopticpy`, while `synopticpy` may still remain useful for interactive or exploratory access.
- No project decision has been made yet to remove `synopticpy`; this is a documented direction for further evaluation rather than a settled workflow choice.
- Retrieved Synoptic QC Types reference data from the `qctypes` endpoint and saved local copies to:
  - [data/synoptic_qctypes.json](/Users/hirschij/Documents/Projects/Wildfire/fmc_data/data/synoptic_qctypes.json)
  - [data/synoptic_qctypes.csv](/Users/hirschij/Documents/Projects/Wildfire/fmc_data/data/synoptic_qctypes.csv)
- Retrieved count from the saved QC Types payload:
  - 83 entries in `QCTYPES`
- Current planning assumption: the free Synoptic token may have a limited historical access window, potentially around the previous year, though the exact limit should be verified with a direct historical request if needed.
- For now, data-access code should remain token-agnostic and avoid hard-coding assumptions that only hold for the current free token.
- Longer-term project direction: the intended production-scale data build is to run the full retrieval pipeline with a paid Synoptic token so the classifier can be trained on the broadest practical historical FMC dataset.
- Added [etc/test_pull_denver_recent_week.yaml](/Users/hirschij/Documents/Projects/Wildfire/fmc_data/etc/test_pull_denver_recent_week.yaml) as the first proposed YAML config file for a bounded Synoptic FMC test pull.
- This first version is intentionally test-focused, using a small Denver-area bounding box and a relative one-week time window.
- Deferred any `decisions.md` update about config-file conventions until we have used and evaluated this first config pattern.
- Created [data/ingest](/Users/hirschij/Documents/Projects/Wildfire/fmc_data/data/ingest:1) as the planned landing area for ingest outputs and added [data/ingest/.ingest](/Users/hirschij/Documents/Projects/Wildfire/fmc_data/data/ingest/.ingest:1) as a tracked placeholder.
- Current plan is to test future FMC retrieval outputs in `data/ingest/` before deciding whether the ingest layout and naming pattern should become a formal project convention.
- Added [src/pull_fmc_timeseries.py](/Users/hirschij/Documents/Projects/Wildfire/fmc_data/src/pull_fmc_timeseries.py) as the first config-driven FMC timeseries pull script.
- Added [tests/test_pull_fmc_timeseries.py](/Users/hirschij/Documents/Projects/Wildfire/fmc_data/tests/test_pull_fmc_timeseries.py) to verify config loading, time resolution, request construction, and the script's progress messages.
- Updated [etc/environment.yml](/Users/hirschij/Documents/Projects/Wildfire/fmc_data/etc/environment.yml) to include `pyyaml`, since the config-driven pull script reads YAML files.
- Updated [etc/test_pull_denver_recent_week.yaml](/Users/hirschij/Documents/Projects/Wildfire/fmc_data/etc/test_pull_denver_recent_week.yaml) to explicitly write outputs to `data/ingest`.
- Added per-run `run.log` output so the pull script writes the same human-readable progress messages to disk that it prints to the console.
- Completed the first successful config-driven FMC test pull using [etc/test_pull_denver_recent_week.yaml](/Users/hirschij/Documents/Projects/Wildfire/fmc_data/etc/test_pull_denver_recent_week.yaml).
- The first test pull wrote outputs to [data/ingest/denver_recent_week_test_2026-04-16T214915Z](/Users/hirschij/Documents/Projects/Wildfire/fmc_data/data/ingest/denver_recent_week_test_2026-04-16T214915Z:1), including raw JSON, resolved config, CSV, run summary, and run log.
- Retrieved counts from the first test pull:
  - 5 stations returned in the Denver-area bounding box
  - 1344 tabular FMC rows written to the CSV output
- Current ingest planning direction is to support repeated FMC retrieval across multiple bounding boxes and multiple time periods rather than treating each pull as an isolated one-off run.
- A likely next-step requirement is to maintain a shared pool of previously collected FMC data so new pulls can be checked against existing coverage before requesting duplicate data.
- This implies future ingest code should track coverage metadata for each pull, including spatial bounds, time window, request settings, and output location.
- The intended behavior is for retrieval code to detect when a requested spatial-temporal slice has already been collected into the shared pool and avoid unnecessary duplicate pulls.
- The exact structure of the shared pool and duplicate-checking workflow is still under design and is not yet a formal project decision.

## 2026-05-07

- Re-ran the Denver one-week test pull with the updated split-output script and confirmed the current run artifacts now include separate FMC and weather CSV outputs.
- The Denver rerun wrote outputs to [data/ingest/denver_recent_week_test_2026-05-07T035450Z](/Users/hirschij/Documents/Projects/Wildfire/fmc_data/data/ingest/denver_recent_week_test_2026-05-07T035450Z:1).
- Retrieved counts from the Denver rerun:
  - 5 stations returned
  - 1344 FMC rows written
  - 0 weather rows written
- Added [etc/test_pull_seattle_recent_week_allvars.yaml](/Users/hirschij/Documents/Projects/Wildfire/fmc_data/etc/test_pull_seattle_recent_week_allvars.yaml) and [tests/test_pull_allvars_timeseries.py](/Users/hirschij/Documents/Projects/Wildfire/fmc_data/tests/test_pull_allvars_timeseries.py) to exercise an all-available-variables pull over a Seattle-area bounding box while preserving separate FMC and weather outputs.
- Initial Seattle all-variables live pull using only bbox selection returned a much broader station pool than intended, demonstrating that unrestricted all-variable retrieval can be dominated by non-FMC weather stations.
- Updated [src/pull_fmc_timeseries.py](/Users/hirschij/Documents/Projects/Wildfire/fmc_data/src/pull_fmc_timeseries.py) so `selection.require_fmc_stations: true` triggers a metadata pre-query for `vars=fuel_moisture`, then uses the resulting FMC-capable station list as the selector for the all-variables timeseries pull.
- Updated the Seattle test config to explicitly require FMC-capable stations before requesting all available variables.
- Verified locally that the Denver and Seattle automated tests both pass after the FMC-station filtering change.
- Re-ran the Seattle all-variables pull with FMC-station filtering enabled and wrote outputs to [data/ingest/seattle_recent_week_allvars_test_2026-05-07T162328Z](/Users/hirschij/Documents/Projects/Wildfire/fmc_data/data/ingest/seattle_recent_week_allvars_test_2026-05-07T162328Z:1).
- Retrieved counts from the filtered Seattle run:
  - 8 FMC-capable stations found in the Seattle bounding box
  - 8 stations returned by the all-variables timeseries request
  - 168 FMC rows written
  - 106849 weather rows written
- The filtered Seattle result confirmed the intended retrieval pattern for co-located weather context: pull weather variables only for stations that are already known to carry FMC observations.
- Current implementation direction is to organize merged training data as file-based pooled datasets rather than introducing a full database layer at this stage.
- The tentative pooled-data structure is:
  - raw run artifacts remain under `data/ingest/`
  - pooled FMC observations, pooled co-located weather observations, pooled station metadata, and pooled coverage metadata will be built as shared file-based datasets
- Current preferred format for the pooled shared datasets is Parquet rather than CSV, primarily for scale, type stability, and repeated analytical reads.
- No pooled-data implementation has been created yet; this is the current intended next step for turning repeated Synoptic ingest runs into model-training inputs.
- Added [etc/gacc_pull_configs](/Users/hirschij/Documents/Projects/Wildfire/fmc_data/etc/gacc_pull_configs:1) as a dedicated directory for region-specific Synoptic retrieval configs.
- Created one initial recent-week all-variable retrieval config per western GACC, each restricted to FMC-capable stations and writing to `data/ingest/`.
- Updated the GACC retrieval config naming to be more general than a repeated latest-week workflow.
- Current naming convention for these retrieval configs is `<gacc_code>_<variable_mode>.yaml`, for example [nwcc_allvars.yaml](/Users/hirschij/Documents/Projects/Wildfire/fmc_data/etc/gacc_pull_configs/nwcc_allvars.yaml:1).
- The reusable GACC config filenames are intended to stay stable even when the time window inside the file changes for a specific retrieval campaign.
- The current GACC configs still express region selection through explicit bounding boxes because the pull script does not yet resolve GACC names into bounding boxes automatically.
- Each GACC config now also records `selection.gacc` explicitly so downstream pooling and manifest logic can preserve the intended regional label even before automatic GACC-to-bbox resolution is implemented.

## 2026-05-10

- Discussed historical training-data strategy for the FMC sensor-validity classifier.
- Synoptic requires a paid token for older historical data, but the project has access to a historical FMC data stash maintained by the Wildfire Interdisciplinary Research Center (WIRC).
- The WIRC stash includes a portion of labeled data based on the historical stash and will be used to train the classifier.
- Project contact for the WIRC stash is Angel Farguell-Caus.
- The stash did not record all available sensor data, so feature design and model evaluation should account for differences between the historical stash and future Synoptic retrievals.
- Existing Synoptic API retrieval code will continue to be used to pull new data and test real-time classification behavior on newly retrieved FMC observations.

## 2026-05-12

- Identified manually labeled FMC validity datasets in [data/labeled](/Users/hirschij/Documents/Projects/Wildfire/fmc_data/data/labeled:1).
- The current labeled CSVs are organized by region and use interval records with `stid`, `start`, `end`, and `valid` fields to mark valid and invalid fuel-moisture sensor periods.
- These manually labeled valid/invalid intervals are intended to be used as training labels for the FMC sensor-validity classifier.

## 2026-05-19

- Discussed weather-context needs for diagnosing valid and invalid FMC behavior, especially cases where flat FMC may indicate rain or wetting rather than a failed sensor.
- Decided to use historical HRRR weather-model data as the initial historical weather-context source for classifier training instead of paying for older Synoptic station-observation access at this stage.
- Added historical HRRR stash data under [data/hrrr_stash](/Users/hirschij/Documents/Projects/Wildfire/fmc_data/data/hrrr_stash:1).
- Initial inspection found regional pickle files:
  - `ml_nw.pkl`
  - `ml_nr.pkl`
  - `ml_rocky.pkl`
  - `ml_gb.pkl`
  - `ml_sw.pkl`
  - `ml_ca.pkl`
- The readable HRRR regional files are station-keyed dictionaries where each station entry includes a `data` DataFrame and `units` metadata.
- The HRRR station data include hourly 2023-2024 records with weather/model fields such as `rain`, `rh`, `temp`, `wind`, `Ed`, `Ew`, HRRR grid coordinates, and source station/grid metadata.
- Initial inspection found that [data/hrrr_stash/ml_ca.pkl](/Users/hirschij/Documents/Projects/Wildfire/fmc_data/data/hrrr_stash/ml_ca.pkl:1) currently raises `EOFError: Ran out of input` when loaded with Python pickle, so California HRRR stash availability needs follow-up.
- Added [src/hrrr_stash.py](/Users/hirschij/Documents/Projects/Wildfire/fmc_data/src/hrrr_stash.py) as the reusable HRRR stash reader.
- Added [src/pull_hrrr_timeseries.py](/Users/hirschij/Documents/Projects/Wildfire/fmc_data/src/pull_hrrr_timeseries.py) as a config-driven script for writing HRRR weather ingest artifacts.
- Added [etc/test_pull_hrrr_stash_swcc_2023_day.yaml](/Users/hirschij/Documents/Projects/Wildfire/fmc_data/etc/test_pull_hrrr_stash_swcc_2023_day.yaml) as the first HRRR stash config, targeting SWCC station `QBAA3` on 2023-01-07.
- Added [tests/test_hrrr_stash.py](/Users/hirschij/Documents/Projects/Wildfire/fmc_data/tests/test_hrrr_stash.py) to verify HRRR config loading, in-memory query behavior, and script output behavior.
- Verified the HRRR reader and script with `/opt/anaconda3/envs/fmc_synoptic/bin/python tests/test_hrrr_stash.py`.
- The HRRR test loaded one SWCC source file, selected one station, wrote 24 hourly weather rows, and preserved units metadata including `rain: kg m-2`.
- Verified syntax with `/opt/anaconda3/envs/fmc_synoptic/bin/python -m py_compile src/hrrr_stash.py src/pull_hrrr_timeseries.py tests/test_hrrr_stash.py`.

## 2026-06-03

- Proposed a targeted plan for constructing train/validation/test datasets from the stashed RAWS FMC data, HRRR-backed ML data objects, and manual FMC validity labels.
- The intended supervised row unit is an hourly FMC observation joined to weather-context features and assigned a valid/invalid target from manual interval labels.
- Current plan is to use the HRRR ML objects as the first training-data backbone because they already join RAWS FMC observations to HRRR weather features at station locations.
- Current plan is to use the MesoDB/RAWS stash initially as a reconciliation and backfill source rather than as the first canonical training backbone.
- Clarified cross-validation direction: use leave-one-GACC-out evaluation, where one GACC at a time is held out as the test set.
- Intended leave-one-GACC-out folds should eventually loop over every usable GACC so each region takes a turn as the held-out test region.
- Within each fold, split the non-held-out GACCs into training and validation sets using station-grouped, seed-controlled splits so all observations from a station remain in only one split.
- Planned repeated runs with different random seeds are intended to estimate classifier uncertainty due to train/validation sampling and model-training stochasticity.
- Important evaluation caveat: the held-out GACC test set is fixed within a fold, so seed replications estimate training-process variability, while differences across held-out GACCs estimate spatial/regional generalization.
- Current usable labeled/HRRR GACC set appears to include GBCC, NRCC, RMCC/Rocky, and SWCC; California remains blocked by the unreadable `ml_ca.pkl`, and additional regions should be included only when matching labels and readable HRRR inputs are available.
- The proposed dataset builder should emit a manifest recording held-out GACC, random seed, station split assignment, label counts, valid/invalid hour counts, source files, and any dropped/missing station-time rows.

## 2026-06-24

- Discussed literature framing for the FMC sensor-validity classifier.
- The broader methodological literature is anomaly detection, especially sensor fault detection, automated sensor-observation quality control, and sensor data validation.
- The closest project match is not generic time-series classification, but real-time or near-real-time identification of broken, anomalous, or invalid sensor observations before downstream use.
- Some closely related work starts from manual or expert QC labels, such as DeepQC for in-situ soil-moisture sensor time-series QC, while other approaches learn normal behavior and flag deviations or use model residuals from expected-value predictions.
- The project's planned framing remains supervised valid/invalid FMC observation classification using manually labeled intervals, with weather context to reduce false positives where unusual FMC behavior is meteorologically plausible.
- Refined the literature-review scope toward time-series-based methods because FMC sensor validity usually cannot be judged from an isolated hourly value alone.
- Temporal context is expected to be important for detecting failure modes such as flatlining, implausible jumps, degraded response, or behavior that is only suspicious relative to preceding values and weather context.
- For real-time classification, the most directly relevant methods are those that use current and prior observations; methods using future observations may still be relevant for delayed or retrospective QC but are less directly aligned with immediate real-time flagging.
- Spatial comparison methods and static instant-only classifiers may be useful background citations, but they are not the central methodological target unless they incorporate temporal-window features or sequence structure.
- Discussed candidate ML model families for the initial FMC sensor-validity classifier.
- Current model-development scope should focus on methods that are practical to implement and tune within an ML workflow: a simple supervised baseline, RNN/LSTM sequence classifiers, and Transformer/attention-based sequence classifiers.
- The simple baseline should still receive temporal-window information through engineered features such as recent FMC values, differences, rolling variability, flatline duration, and weather-context summaries, so comparisons against sequence models are meaningful.
- RNN/LSTM models are a natural first deep-learning candidate because they directly model ordered FMC/weather sequences and can output a calibrated or thresholded probability of valid or invalid sensor data.
- Transformer or attention-based models are a useful second sequence-model family to consider, especially for longer temporal context or nonlocal dependencies, but may require more data and tuning than LSTM-style models.
- Other statistical QC and anomaly-detection approaches remain useful background, but are not the current primary implementation focus.
- Discussed fixed-window versus stateful sequence modeling for the FMC sensor-validity classifier.
- Candidate lookback windows should include 24, 48, and 72 hours. These lengths are computationally manageable and physically motivated because they capture one to three diurnal cycles in FMC and weather response.
- Initial training should use fixed, assumed-independent windows rather than long stateful station histories. This independence assumption is a simplifying modeling choice that avoids the complexity of stateful training across long, irregular sensor records.
- For RNN/LSTM validation and testing, streaming prediction should be considered: initialize from a recent window, carry recurrent state forward, and classify each new hourly observation as it arrives. This can support efficient real-time operation and may improve accuracy by carrying information beyond the strict fixed training window.
- Streaming validation/test inference departs from the exact fixed-window representation used during training, so this should be treated as an explicit inference-mode choice and compared against fixed-window validation where practical.
- Long-lived stateful training is not the current preferred approach because real sensor records contain invalid periods, outages, maintenance gaps, and other discontinuities that make hidden-state management cumbersome.
- This choice is also informed by prior experience with stateful modeling in the `ml_fmda` project, where long-term stateful training was explored and found too cumbersome for practical training workflows.
