from hindcast import run_hindcast


def test_hindcast_output():
    request = {
        "incident_id": "INC001",
        "centroid": [74.81, 12.51],
        "detection_time": "2026-08-30T12:00:00Z",
        "spill_geojson": {},
        "hours_back": 24
    }

    result = run_hindcast(request)

    assert result["incident_id"] == "INC001"

    assert result["trajectory"]["type"] == "Feature"
    assert result["trajectory"]["geometry"]["type"] == "LineString"

    assert len(
        result["trajectory"]["geometry"]["coordinates"]
    ) > 0

    assert result["source_corridor"]["type"] == "Feature"
    assert result["source_corridor"]["geometry"]["type"] == "Polygon"

    assert len(
        result["source_corridor"]["geometry"]["coordinates"]
    ) > 0


def test_hindcast_fallback():
    request = {
        "incident_id": "FALLBACK01",
        "centroid": [74.81, 12.51],
        "detection_time": "2026-08-30T12:00:00Z",
        "spill_geojson": {},
        "hours_back": 24
    }

    result = run_hindcast(request)

    assert result["incident_id"] == "FALLBACK01"
    assert result["trajectory"]["type"] == "Feature"
    assert result["trajectory"]["geometry"]["type"] == "LineString"

    assert len(
        result["trajectory"]["geometry"]["coordinates"]
    ) > 0

    assert result["source_corridor"]["type"] == "Feature"
    assert result["source_corridor"]["geometry"]["type"] == "Polygon"


def test_person_b_handoff():
    request = {
        "incident_id": "HANDOFF01",
        "centroid": [74.81, 12.51],
        "detection_time": "2026-08-30T12:00:00Z",
        "spill_geojson": {},
        "hours_back": 24
    }

    result = run_hindcast(request)

    assert "incident_id" in result
    assert "trajectory" in result
    assert "source_corridor" in result

    assert result["trajectory"]["geometry"]["type"] == "LineString"
    assert result["source_corridor"]["geometry"]["type"] == "Polygon"

def test_wind_data_available():
    import xarray as xr

    ds = xr.open_dataset("outputs/indian_ocean_wind_24h.nc")

    assert "x_wind" in ds.data_vars
    assert "y_wind" in ds.data_vars

    assert len(ds.time) > 0
    assert len(ds.latitude) > 0
    assert len(ds.longitude) > 0

    ds.close()

    print("Wind data test passed!")