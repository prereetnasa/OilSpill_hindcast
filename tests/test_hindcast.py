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
    print("\nFINAL HINDCAST OUTPUT:")
    print(result)

    # Check incident ID
    assert result["incident_id"] == "INC001"

    # Check trajectory
    assert result["trajectory"]["type"] == "Feature"
    assert result["trajectory"]["geometry"]["type"] == "LineString"

    # Check trajectory has coordinates
    assert len(
        result["trajectory"]["geometry"]["coordinates"]
    ) > 0

    # Check source corridor
    assert result["source_corridor"]["type"] == "Feature"
    assert result["source_corridor"]["geometry"]["type"] == "Polygon"

    # Check corridor has coordinates
    assert len(
        result["source_corridor"]["geometry"]["coordinates"]
    ) > 0

    print("Hindcast contract test passed!")


if __name__ == "__main__":
    test_hindcast_output()
    print("All tests passed!")
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
    assert len(result["trajectory"]["geometry"]["coordinates"]) > 0
    assert result["source_corridor"]["type"] == "Feature"
    assert result["source_corridor"]["geometry"]["type"] == "Polygon"

    print("Fallback/output schema test passed!")