from __future__ import annotations

import argparse
import csv
import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import requests

try:
    import yaml
except ImportError as exc:  # pragma: no cover - import-time guidance
    raise SystemExit(
        "PyYAML is required to read YAML configs. Install pyyaml in the active environment."
    ) from exc


ROOT = Path("/Users/hirschij/Documents/Projects/Wildfire/fmc_data")
TOKENS_PATH = ROOT / "etc" / "tokens.json"
SYNOPTIC_TIMESERIES_URL = "https://api.synopticdata.com/v2/stations/timeseries"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Pull Synoptic fuel moisture timeseries data from a YAML config."
    )
    parser.add_argument(
        "config",
        type=Path,
        help="Path to a YAML config file.",
    )
    return parser.parse_args()


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open() as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError(f"Config at {path} must parse to a mapping.")
    return data


def load_token(tokens_path: Path) -> str:
    with tokens_path.open() as f:
        data = json.load(f)
    token = data.get("synoptic_api_token")
    if not token:
        raise ValueError(f"Expected 'synoptic_api_token' in {tokens_path}.")
    return token


def resolve_time_window(config: dict[str, Any]) -> tuple[datetime, datetime]:
    time_config = config.get("time", {})
    mode = time_config.get("mode")

    if mode != "relative":
        raise ValueError(f"Unsupported time.mode={mode!r}. Only 'relative' is supported in v1.")

    recent = time_config.get("recent", {})
    days = recent.get("days")
    if days is None:
        raise ValueError("Expected time.recent.days in the config.")

    end = datetime.now(UTC).replace(microsecond=0)
    start = end - timedelta(days=int(days))
    return start, end


def build_request_params(config: dict[str, Any], token: str, start: datetime, end: datetime) -> dict[str, Any]:
    selection = config.get("selection", {})
    request = config.get("request", {})
    bbox = selection.get("bbox", {})
    vars_requested = selection.get("vars", [])

    required_bbox_keys = {"lon_min", "lat_min", "lon_max", "lat_max"}
    missing = required_bbox_keys - set(bbox)
    if missing:
        raise ValueError(f"Missing bbox keys: {sorted(missing)}")

    if not vars_requested:
        raise ValueError("Expected at least one variable in selection.vars.")

    params: dict[str, Any] = {
        "token": token,
        "bbox": f"{bbox['lon_min']},{bbox['lat_min']},{bbox['lon_max']},{bbox['lat_max']}",
        "vars": ",".join(vars_requested),
        "start": start.strftime("%Y%m%d%H%M"),
        "end": end.strftime("%Y%m%d%H%M"),
    }

    for key in ("complete", "sensorvars", "status"):
        if key in request:
            value = request[key]
            if isinstance(value, bool):
                params[key] = int(value)
            else:
                params[key] = value

    return params


def make_run_dir(config: dict[str, Any], output_dir: str, run_time: datetime) -> Path:
    output = config.get("output", {})
    tag = output.get("tag") or config.get("name") or "fmc_pull"
    run_stamp = run_time.strftime("%Y-%m-%dT%H%M%SZ")
    run_dir = ROOT / output_dir / f"{tag}_{run_stamp}"
    run_dir.mkdir(parents=True, exist_ok=False)
    return run_dir


def flatten_timeseries(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    for station in payload.get("STATION", []):
        base = {
            "stid": station.get("STID"),
            "station_name": station.get("NAME"),
            "station_id": station.get("ID"),
            "mnet_id": station.get("MNET_ID"),
            "state": station.get("STATE"),
            "timezone": station.get("TIMEZONE"),
            "status": station.get("STATUS"),
            "latitude": station.get("LATITUDE"),
            "longitude": station.get("LONGITUDE"),
            "elevation": station.get("ELEVATION"),
            "period_start": (station.get("PERIOD_OF_RECORD") or {}).get("start"),
            "period_end": (station.get("PERIOD_OF_RECORD") or {}).get("end"),
        }

        observations = station.get("OBSERVATIONS", {})
        date_times = observations.get("date_time", [])

        value_keys = [
            key for key in observations
            if key != "date_time" and key.startswith("fuel_moisture")
        ]

        for key in value_keys:
            values = observations.get(key, [])
            for index, date_time in enumerate(date_times):
                value = values[index] if index < len(values) else None
                rows.append(
                    base
                    | {
                        "date_time": date_time,
                        "sensor_key": key,
                        "fuel_moisture": value,
                    }
                )

    return rows


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if rows:
        fieldnames = list(rows[0].keys())
    else:
        fieldnames = [
            "stid",
            "station_name",
            "station_id",
            "mnet_id",
            "state",
            "timezone",
            "status",
            "latitude",
            "longitude",
            "elevation",
            "period_start",
            "period_end",
            "date_time",
            "sensor_key",
            "fuel_moisture",
        ]

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def make_logger(log_path: Path):
    def log(message: str) -> None:
        print(message)
        with log_path.open("a", encoding="utf-8") as f:
            f.write(message + "\n")

    return log


def main() -> int:
    args = parse_args()
    config_path = args.config.resolve()
    config = load_yaml(config_path)
    token = load_token(TOKENS_PATH)
    start, end = resolve_time_window(config)
    output_dir = config.get("output", {}).get("output_dir", "data/ingest")
    run_dir = make_run_dir(config, output_dir, datetime.now(UTC))
    log = make_logger(run_dir / "run.log")
    log(f"Loaded config: {config_path}")
    log(f"Config name: {config.get('name', '<unnamed>')}")
    log(f"Loaded Synoptic token from: {TOKENS_PATH}")
    log(
        "Resolved time window: "
        f"{start.isoformat().replace('+00:00', 'Z')} to "
        f"{end.isoformat().replace('+00:00', 'Z')}"
    )
    log(f"Created run directory: {run_dir}")

    params = build_request_params(config, token, start, end)
    log("Prepared Synoptic request parameters:")
    log(f"  service: {config.get('request', {}).get('service', 'timeseries')}")
    log(f"  bbox: {params.get('bbox')}")
    log(f"  vars: {params.get('vars')}")
    log(f"  start: {params.get('start')}")
    log(f"  end: {params.get('end')}")
    if "status" in params:
        log(f"  status: {params.get('status')}")
    if "complete" in params:
        log(f"  complete: {params.get('complete')}")
    if "sensorvars" in params:
        log(f"  sensorvars: {params.get('sensorvars')}")

    log("Requesting Synoptic timeseries data...")
    response = requests.get(SYNOPTIC_TIMESERIES_URL, params=params, timeout=120)
    response.raise_for_status()
    payload = response.json()

    if payload.get("SUMMARY", {}).get("RESPONSE_CODE") != 1:
        raise RuntimeError(payload.get("SUMMARY", {}).get("RESPONSE_MESSAGE", "Synoptic request failed."))

    response_summary = payload.get("SUMMARY", {})
    station_count = len(payload.get("STATION", []))
    log("Received Synoptic response:")
    log(f"  response_code: {response_summary.get('RESPONSE_CODE')}")
    log(f"  response_message: {response_summary.get('RESPONSE_MESSAGE')}")
    log(f"  station_count: {station_count}")

    raw_json_path = run_dir / "raw_timeseries.json"
    raw_json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    log(f"Wrote raw JSON: {raw_json_path}")

    resolved_config = json.loads(json.dumps(config))
    resolved_config["resolved_time"] = {
        "start_utc": start.isoformat().replace("+00:00", "Z"),
        "end_utc": end.isoformat().replace("+00:00", "Z"),
    }
    resolved_config["request_params"] = params | {"token": "<redacted>"}
    (run_dir / "resolved_config.json").write_text(
        json.dumps(resolved_config, indent=2),
        encoding="utf-8",
    )
    log(f"Wrote resolved config: {run_dir / 'resolved_config.json'}")

    rows = flatten_timeseries(payload)
    timeseries_csv_path = run_dir / "timeseries.csv"
    write_csv(timeseries_csv_path, rows)
    log(f"Wrote tabular CSV: {timeseries_csv_path}")

    summary = {
        "config_path": str(config_path),
        "run_dir": str(run_dir),
        "station_count": station_count,
        "row_count": len(rows),
        "response_summary": response_summary,
        "resolved_time": resolved_config["resolved_time"],
    }
    run_summary_path = run_dir / "run_summary.json"
    run_summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    log(f"Wrote run summary: {run_summary_path}")

    log("Run completed successfully:")
    log(f"  stations returned: {summary['station_count']}")
    log(f"  rows written: {summary['row_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
