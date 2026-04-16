from __future__ import annotations

import importlib.util
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace


ROOT = Path("/Users/hirschij/Documents/Projects/Wildfire/fmc_data")
MODULE_PATH = ROOT / "src" / "pull_fmc_timeseries.py"
CONFIG_PATH = ROOT / "etc" / "test_pull_denver_recent_week.yaml"


def load_module():
    spec = importlib.util.spec_from_file_location("pull_fmc_timeseries", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {MODULE_PATH}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_test_config_loads_and_resolves():
    module = load_module()

    config = module.load_yaml(CONFIG_PATH)

    assert config["name"] == "denver_recent_week_test"
    assert config["selection"]["vars"] == ["fuel_moisture"]
    assert config["selection"]["bbox"] == {
        "lon_min": -105.35,
        "lat_min": 39.55,
        "lon_max": -104.55,
        "lat_max": 40.15,
    }
    assert config["time"]["mode"] == "relative"
    assert config["time"]["recent"]["days"] == 7

    start, end = module.resolve_time_window(config)

    assert start.tzinfo == UTC
    assert end.tzinfo == UTC
    assert end > start
    assert (end - start).days == 7


def test_request_params_from_test_config():
    module = load_module()

    config = module.load_yaml(CONFIG_PATH)
    start = datetime(2026, 4, 10, 12, 0, tzinfo=UTC)
    end = datetime(2026, 4, 17, 12, 0, tzinfo=UTC)

    params = module.build_request_params(
        config=config,
        token="fake-token",
        start=start,
        end=end,
    )

    assert params["token"] == "fake-token"
    assert params["bbox"] == "-105.35,39.55,-104.55,40.15"
    assert params["vars"] == "fuel_moisture"
    assert params["start"] == "202604101200"
    assert params["end"] == "202604171200"
    assert params["complete"] == 1
    assert params["sensorvars"] == 1
    assert params["status"] == "active"


def test_main_prints_progress_messages(monkeypatch, tmp_path, capsys):
    module = load_module()

    run_dir = tmp_path / "denver_recent_week_test_2026-04-16T120000Z"
    run_dir.mkdir()

    payload = {
        "SUMMARY": {
            "RESPONSE_CODE": 1,
            "RESPONSE_MESSAGE": "OK",
        },
        "STATION": [
            {
                "STID": "TEST1",
                "NAME": "Test Station",
                "ID": "123",
                "MNET_ID": "2",
                "STATE": "CO",
                "TIMEZONE": "America/Denver",
                "STATUS": "ACTIVE",
                "LATITUDE": "39.75",
                "LONGITUDE": "-104.95",
                "ELEVATION": "5280",
                "PERIOD_OF_RECORD": {
                    "start": "2026-04-10T00:00:00Z",
                    "end": "2026-04-17T00:00:00Z",
                },
                "OBSERVATIONS": {
                    "date_time": [
                        "2026-04-16T12:00:00Z",
                        "2026-04-16T13:00:00Z",
                    ],
                    "fuel_moisture_set_1": [9.1, 9.3],
                },
            }
        ],
    }

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return payload

    monkeypatch.setattr(
        module,
        "parse_args",
        lambda: SimpleNamespace(config=CONFIG_PATH),
    )
    monkeypatch.setattr(module, "load_token", lambda _: "fake-token")
    monkeypatch.setattr(module, "make_run_dir", lambda *args, **kwargs: run_dir)
    monkeypatch.setattr(module.requests, "get", lambda *args, **kwargs: FakeResponse())

    exit_code = module.main()
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Loaded config:" in captured.out
    assert "Config name: denver_recent_week_test" in captured.out
    assert "Resolved time window:" in captured.out
    assert "Prepared Synoptic request parameters:" in captured.out
    assert "Requesting Synoptic timeseries data..." in captured.out
    assert "Received Synoptic response:" in captured.out
    assert "response_message: OK" in captured.out
    assert "Wrote raw JSON:" in captured.out
    assert "Wrote resolved config:" in captured.out
    assert "Wrote tabular CSV:" in captured.out
    assert "Wrote run summary:" in captured.out
    assert "Run completed successfully:" in captured.out
    assert "stations returned: 1" in captured.out
    assert "rows written: 2" in captured.out
