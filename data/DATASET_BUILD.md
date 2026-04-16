# Dataset Build

This document records how to recreate the Synoptic-derived datasets currently stored in `data/`.

## Prerequisites

- Activate the dedicated data-processing environment:

```bash
conda activate fmc_synoptic
```

- Ensure a live Synoptic token is available in:

```text
etc/tokens.json
```

- The current token file is expected to have this key:

```json
{
  "synoptic_api_token": "..."
}
```

## 1. Synoptic Variables

Produces:

- `data/synoptic_variables.json`
- `data/synoptic_variables.csv`

Command:

```bash
python - <<'PY'
import csv
import json
from pathlib import Path
import requests

root = Path("/Users/hirschij/Documents/Projects/Wildfire/fmc_data")
token = json.loads((root / "etc" / "tokens.json").read_text())["synoptic_api_token"]

url = "https://api.synopticdata.com/v2/variables"
payload = requests.get(url, params={"token": token}, timeout=60).json()

(root / "data" / "synoptic_variables.json").write_text(
    json.dumps(payload, indent=2),
    encoding="utf-8",
)

rows = []
for item in payload.get("VARIABLES", []):
    variable_name, meta = next(iter(item.items()))
    rows.append(
        {
            "variable_name": variable_name,
            "vid": meta.get("vid"),
            "long_name": meta.get("long_name"),
            "unit": meta.get("unit"),
        }
    )

with (root / "data" / "synoptic_variables.csv").open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["variable_name", "vid", "long_name", "unit"])
    writer.writeheader()
    writer.writerows(rows)
PY
```

## 2. Synoptic Networks

Produces:

- `data/synoptic_networks.json`
- `data/synoptic_networks.csv`

Command:

```bash
python - <<'PY'
import csv
import json
from pathlib import Path
import requests

root = Path("/Users/hirschij/Documents/Projects/Wildfire/fmc_data")
token = json.loads((root / "etc" / "tokens.json").read_text())["synoptic_api_token"]

url = "https://api.synopticdata.com/v2/networks"
payload = requests.get(url, params={"token": token}, timeout=60).json()

(root / "data" / "synoptic_networks.json").write_text(
    json.dumps(payload, indent=2),
    encoding="utf-8",
)

fieldnames = [
    "id",
    "shortname",
    "longname",
    "url",
    "citation",
    "program",
    "category",
    "last_observation",
    "reporting_stations",
    "active_stations",
    "total_stations",
    "percent_active",
    "percent_reporting",
    "period_checked",
    "active_restricted",
    "total_restricted",
    "period_of_record_start",
    "period_of_record_end",
]

rows = []
for item in payload.get("MNET", []):
    rows.append(
        {
            "id": item.get("ID"),
            "shortname": item.get("SHORTNAME"),
            "longname": item.get("LONGNAME"),
            "url": item.get("URL"),
            "citation": item.get("CITATION"),
            "program": item.get("PROGRAM"),
            "category": item.get("CATEGORY"),
            "last_observation": item.get("LAST_OBSERVATION"),
            "reporting_stations": item.get("REPORTING_STATIONS"),
            "active_stations": item.get("ACTIVE_STATIONS"),
            "total_stations": item.get("TOTAL_STATIONS"),
            "percent_active": item.get("PERCENT_ACTIVE"),
            "percent_reporting": item.get("PERCENT_REPORTING"),
            "period_checked": item.get("PERIOD_CHECKED"),
            "active_restricted": item.get("ACTIVE_RESTRICTED"),
            "total_restricted": item.get("TOTAL_RESTRICTED"),
            "period_of_record_start": (item.get("PERIOD_OF_RECORD") or {}).get("start"),
            "period_of_record_end": (item.get("PERIOD_OF_RECORD") or {}).get("end"),
        }
    )

with (root / "data" / "synoptic_networks.csv").open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)
PY
```

## 3. Stations With Fuel Moisture Metadata

Produces:

- `data/synoptic_stations_fuel_moisture.json`
- `data/synoptic_stations_fuel_moisture.csv`

Notes:

- This uses the station metadata endpoint with `vars=fuel_moisture`.
- Include `sensorvars=1` so the response explicitly includes `fuel_moisture` sensor metadata.

Command:

```bash
python - <<'PY'
import csv
import json
from pathlib import Path
import requests

root = Path("/Users/hirschij/Documents/Projects/Wildfire/fmc_data")
token = json.loads((root / "etc" / "tokens.json").read_text())["synoptic_api_token"]

url = "https://api.synopticdata.com/v2/stations/metadata"
params = {
    "token": token,
    "vars": "fuel_moisture",
    "sensorvars": 1,
}
payload = requests.get(url, params=params, timeout=120).json()

(root / "data" / "synoptic_stations_fuel_moisture.json").write_text(
    json.dumps(payload, indent=2),
    encoding="utf-8",
)

fieldnames = [
    "stid",
    "station_name",
    "state",
    "country",
    "latitude",
    "longitude",
    "elevation",
    "timezone",
    "status",
    "mnet_id",
    "mnet_name",
    "period_start",
    "period_end",
    "has_fuel_moisture",
    "fuel_moisture_sensor_count",
    "fuel_moisture_sensor_names",
]

rows = []
for item in payload.get("STATION", []):
    sensor_variables = item.get("SENSOR_VARIABLES") or {}
    fuel_meta = sensor_variables.get("fuel_moisture") or {}
    rows.append(
        {
            "stid": item.get("STID"),
            "station_name": item.get("NAME"),
            "state": item.get("STATE"),
            "country": item.get("COUNTRY"),
            "latitude": item.get("LATITUDE"),
            "longitude": item.get("LONGITUDE"),
            "elevation": item.get("ELEVATION"),
            "timezone": item.get("TIMEZONE"),
            "status": item.get("STATUS"),
            "mnet_id": item.get("MNET_ID"),
            "mnet_name": item.get("MNET_LONGNAME") or item.get("MNET_NAME"),
            "period_start": (item.get("PERIOD_OF_RECORD") or {}).get("start"),
            "period_end": (item.get("PERIOD_OF_RECORD") or {}).get("end"),
            "has_fuel_moisture": "fuel_moisture" in sensor_variables,
            "fuel_moisture_sensor_count": len(fuel_meta),
            "fuel_moisture_sensor_names": "|".join(sorted(fuel_meta.keys())),
        }
    )

with (root / "data" / "synoptic_stations_fuel_moisture.csv").open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)
PY
```
