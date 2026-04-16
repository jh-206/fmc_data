from __future__ import annotations

from datetime import datetime, timedelta, timezone

from synoptic.services import stations_timeseries


def test_synoptic_fuel_moisture_access():
    """Verify SynopticPy can retrieve a recent time series response."""
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=2)

    # Replace with a known RAWS station once the project station list is finalized.
    stid = "WBB"

    df = stations_timeseries(
        stid=stid,
        start=start.strftime("%Y%m%d%H%M"),
        end=end.strftime("%Y%m%d%H%M"),
    )

    assert df is not None
    assert hasattr(df, "columns")
    assert len(df) > 0

    column_names = [str(col).lower() for col in df.columns]
    assert any("fuel" in col or "moisture" in col for col in column_names)
