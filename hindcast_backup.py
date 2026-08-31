from shapely.geometry import LineString
import json

# -----------------------------
# TEAM 1 INPUT (dummy for now)
# -----------------------------
centroid = [74.81, 12.51]
detection_time = "2026-08-30T12:00:00Z"


# -----------------------------
# Create backward trajectory
# -----------------------------
def create_demo_trajectory(centroid, hours_back=24):
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


# -----------------------------
# Convert trajectory to GeoJSON
# -----------------------------
coordinates = create_demo_trajectory(centroid)

line = LineString(coordinates)

trajectory_geojson = {
    "type": "Feature",
    "geometry": {
        "type": "LineString",
        "coordinates": list(line.coords)
    },
    "properties": {
        "incident_id": "INC001",
        "detection_time": detection_time
    }
}


# -----------------------------
# Print GeoJSON
# -----------------------------
print("=== TRAJECTORY GEOJSON ===")
print(json.dumps(trajectory_geojson, indent=2))
from shapely.geometry import LineString, mapping
from pyproj import Transformer
import json


def create_source_corridor(coordinates, buffer_km=5):
    """
    Create a probable source corridor around the trajectory.

    buffer_km = width of corridor around the trajectory in kilometres.
    """

    # Create trajectory line
    line = LineString(coordinates)

    # Determine UTM zone from the first coordinate
    lon, lat = coordinates[0]

    utm_zone = int((lon + 180) / 6) + 1
    utm_epsg = 32600 + utm_zone  # Northern hemisphere

    # Convert longitude/latitude → metres
    to_utm = Transformer.from_crs(
        "EPSG:4326",
        f"EPSG:{utm_epsg}",
        always_xy=True
    )

    # Convert metres → longitude/latitude
    to_wgs84 = Transformer.from_crs(
        f"EPSG:{utm_epsg}",
        "EPSG:4326",
        always_xy=True
    )

    # Project trajectory into metres
    projected_coordinates = [
        to_utm.transform(lon, lat)
        for lon, lat in coordinates
    ]

    projected_line = LineString(projected_coordinates)

    # Create 5 km buffer
    corridor = projected_line.buffer(buffer_km * 1000)

    # Convert corridor back to longitude/latitude
    corridor_wgs84 = [
        to_wgs84.transform(x, y)
        for x, y in corridor.exterior.coords
    ]

    return {
        "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": [corridor_wgs84]
        },
        "properties": {
            "buffer_km": buffer_km
        }
    }


# -----------------------------
# CREATE SOURCE CORRIDOR
# -----------------------------

source_corridor = create_source_corridor(
    coordinates,
    buffer_km=5
)


# -----------------------------
# PRINT SOURCE CORRIDOR
# -----------------------------

print("\n=== SOURCE CORRIDOR ===")
print(json.dumps(source_corridor, indent=2))

# -----------------------------
# SAVE HINDCAST OUTPUT
# -----------------------------

hindcast_output = {
    "incident_id": "INC001",
    "trajectory": trajectory_geojson,
    "source_corridor": source_corridor
}

with open("outputs/sample_hindcast.geojson", "w") as file:
    json.dump(hindcast_output, file, indent=2)

print("\nSaved successfully!")
print("File: outputs/sample_hindcast.geojson")