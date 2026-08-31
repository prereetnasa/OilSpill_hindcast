from hindcast import run_hindcast


def test_hindcast_output():
    request = {
        "incident_id": "TEST001",
        "centroid": [74.81, 12.51],
        "detection_time": "2026-08-30T12:00:00Z",
        "spill_geojson": {}
    }

    result = run_hindcast(request)

    # Check incident ID
    assert result["incident_id"] == "TEST001"

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