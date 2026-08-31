import json
from pathlib import Path

from shapely.geometry import LineString
from pyproj import Transformer
from datetime import datetime, timedelta

from opendrift.models.oceandrift import OceanDrift
from opendrift.readers import reader_netCDF_CF_generic

# ============================================================
# 1. CREATE DEMO BACKWARD TRAJECTORY
# ============================================================

def create_demo_trajectory(centroid, hours_back=24):
    """
    Create a simple deterministic backward trajectory.

    centroid format:
        [longitude, latitude]

    NOTE:
        This is a development/demo fallback.
        It is NOT a real ocean-drift simulation.
    """

    lon, lat = centroid

    coordinates = []

    for hour in range(hours_back + 1):

        new_lon = lon - (0.01 * hour)
        new_lat = lat + (0.005 * hour)

        coordinates.append([
            round(new_lon, 5),
            round(new_lat, 5)
        ])

    return coordinates


# ============================================================
# 2. CREATE SOURCE CORRIDOR
# ============================================================

def create_source_corridor(coordinates, buffer_km=5):
    """
    Create a buffered source corridor around the trajectory.

    The trajectory is first projected into metres,
    buffered by buffer_km, and then converted back
    to WGS84 longitude/latitude.
    """

    line = LineString(coordinates)

    # Use the first point to determine a suitable UTM zone
    lon, lat = coordinates[0]

    utm_zone = int((lon + 180) / 6) + 1

    # Northern hemisphere
    utm_epsg = 32600 + utm_zone

    # WGS84 -> UTM
    to_utm = Transformer.from_crs(
        "EPSG:4326",
        f"EPSG:{utm_epsg}",
        always_xy=True
    )

    # UTM -> WGS84
    to_wgs84 = Transformer.from_crs(
        f"EPSG:{utm_epsg}",
        "EPSG:4326",
        always_xy=True
    )

    # Convert trajectory coordinates to metres
    projected_coordinates = [
        to_utm.transform(lon, lat)
        for lon, lat in coordinates
    ]

    projected_line = LineString(projected_coordinates)

    # Buffer in metres
    corridor = projected_line.buffer(buffer_km * 1000)

    # Convert polygon back to longitude/latitude
    corridor_coordinates = [
        to_wgs84.transform(x, y)
        for x, y in corridor.exterior.coords
    ]

    return {
        "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": [corridor_coordinates]
        },
        "properties": {
            "buffer_km": buffer_km
        }
    }

def create_opendrift_trajectory(centroid, detection_time, hours_back=24):
    """
    Run an OpenDrift backward simulation using
    real ocean-current data.
    """

    lon, lat = centroid

    o = OceanDrift(loglevel=0)

    # Real Indian Ocean current data
    reader = reader_netCDF_CF_generic.Reader(
        "outputs/indian_ocean_currents_24h.nc"
    )

    o.add_reader(reader)

    # Convert detection time to datetime
    seed_time = datetime.fromisoformat(
        detection_time.replace("Z", "+00:00")
    ).replace(tzinfo=None)

    print("Reader start time:", reader.start_time)
    print("Reader end time:", reader.end_time)
    print("Seeding particle at:", seed_time)

    # Seed at detected spill location
    o.seed_elements(
        lon=lon,
        lat=lat,
        number=1,
        time=seed_time
    )

    # Run backward
    result = o.run(
        duration=timedelta(hours=hours_back),
        time_step=-600,
        time_step_output=600
    )

    # Extract trajectory
    lons = result.lon.values[0]
    lats = result.lat.values[0]

    coordinates = []

    for x, y in zip(lons, lats):
        if x == x and y == y:
            coordinates.append([float(x), float(y)])

    return coordinates
# ============================================================
# 3. RUN HINDCAST
# ============================================================

def run_hindcast(request):
    """
    Main Person A function.

    Input:
        Team 1 compatible request

    Output:
        Team 2 /hindcast compatible response
    """

    incident_id = request["incident_id"]
    centroid = request["centroid"]
    detection_time = request["detection_time"]

    # Look back requested number of hours, default 24
    hours_back = request.get("hours_back", 24)

    # Try OpenDrift first
    try:
        print("Running OpenDrift hindcast...")

        coordinates = create_opendrift_trajectory(
            centroid,
            detection_time,
            hours_back=hours_back
        )

        print("OpenDrift hindcast completed!")

    except Exception as e:
        print("OpenDrift failed:", e)
        print("Using deterministic fallback trajectory.")

        coordinates = create_demo_trajectory(
            centroid,
            hours_back=hours_back
        )

    # Create trajectory GeoJSON
    trajectory_geojson = {
        "type": "Feature",
        "geometry": {
            "type": "LineString",
            "coordinates": coordinates
        },
        "properties": {
            "incident_id": incident_id,
            "detection_time": detection_time
        }
    }

    # Create source corridor
    source_corridor = create_source_corridor(
        coordinates,
        buffer_km=5
    )

    # Final /hindcast response
    return {
        "incident_id": incident_id,
        "trajectory": trajectory_geojson,
        "source_corridor": source_corridor
    }
# ============================================================
# 4. TEST INPUT
# ============================================================

if __name__ == "__main__":

    test_request = {
        "incident_id": "INC001",
        "centroid": [74.81, 12.51],
        "detection_time": "2026-08-30T12:00:00Z",
        "spill_geojson": {}
    }

    result = run_hindcast(test_request)

    print("========================================")
    print("       TEAM 2 PERSON A HINDCAST")
    print("========================================")

    print(json.dumps(result, indent=2))

    # Save fallback output
    output_path = Path("outputs/sample_hindcast.geojson")

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(output_path, "w") as file:
        json.dump(result, file, indent=2)

    print("\n========================================")
    print("Saved:")
    print(output_path)
    print("========================================")