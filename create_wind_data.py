import requests
import numpy as np
import xarray as xr
from pathlib import Path

# ============================================
# WIND DATA SETTINGS
# ============================================

lats = np.arange(12.0, 13.01, 0.25)
lons = np.arange(74.0, 75.01, 0.25)

start_date = "2026-08-29"
end_date = "2026-08-30"

# ============================================
# DOWNLOAD WIND DATA
# ============================================

all_speed = []
all_direction = []

for lat in lats:
    row_speed = []
    row_direction = []

    for lon in lons:

        url = (
            "https://archive-api.open-meteo.com/v1/archive"
            f"?latitude={lat}"
            f"&longitude={lon}"
            f"&start_date={start_date}"
            f"&end_date={end_date}"
            "&hourly=wind_speed_10m,wind_direction_10m"
            "&wind_speed_unit=ms"
            "&timezone=UTC"
        )

        response = requests.get(url)
        response.raise_for_status()

        data = response.json()

        row_speed.append(data["hourly"]["wind_speed_10m"])
        row_direction.append(data["hourly"]["wind_direction_10m"])

    all_speed.append(row_speed)
    all_direction.append(row_direction)

# ============================================
# TIME
# ============================================

times = data["hourly"]["time"]

# Select exactly the same period as current data:
# 2026-08-29 12:00 → 2026-08-30 12:00

selected_indices = [
    i for i, t in enumerate(times)
    if "2026-08-29T12:00" <= t <= "2026-08-30T12:00"
]

times = [times[i] for i in selected_indices]

speed = np.array(all_speed)[:, :, selected_indices]
direction = np.array(all_direction)[:, :, selected_indices]

# ============================================
# CONVERT SPEED + DIRECTION TO U/V
# ============================================

direction_rad = np.deg2rad(direction)

# Meteorological direction = direction wind comes FROM
u_wind = -speed * np.sin(direction_rad)
v_wind = -speed * np.cos(direction_rad)

# Rearrange to:
# time, latitude, longitude

u_wind = np.transpose(u_wind, (2, 0, 1))
v_wind = np.transpose(v_wind, (2, 0, 1))

# ============================================
# CREATE NETCDF
# ============================================

ds = xr.Dataset(
    {
        "x_wind": (
            ("time", "latitude", "longitude"),
            u_wind
        ),
        "y_wind": (
            ("time", "latitude", "longitude"),
            v_wind
        )
    },
    coords={
        "time": np.array(times, dtype="datetime64[ns]"),
        "latitude": lats,
        "longitude": lons
    }
)

# Metadata
ds["x_wind"].attrs = {
    "standard_name": "eastward_wind",
    "long_name": "10 metre eastward wind",
    "units": "m s-1"
}

ds["y_wind"].attrs = {
    "standard_name": "northward_wind",
    "long_name": "10 metre northward wind",
    "units": "m s-1"
}

ds.attrs["source"] = "Open-Meteo historical weather API"
ds.attrs["description"] = "10 metre wind components for OpenDrift"

# ============================================
# SAVE
# ============================================

output_path = Path("outputs/indian_ocean_wind_24h.nc")
output_path.parent.mkdir(parents=True, exist_ok=True)

ds.to_netcdf(output_path)

print("========================================")
print("WIND DATA CREATED")
print("========================================")
print("Saved:", output_path)
print("Time:", times[0], "to", times[-1])
print("Longitude:", lons.min(), "to", lons.max())
print("Latitude:", lats.min(), "to", lats.max())
print("Variables:", list(ds.data_vars))
print("========================================")