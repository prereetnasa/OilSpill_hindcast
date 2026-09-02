import requests
import numpy as np
import xarray as xr
from pathlib import Path
from datetime import datetime, timedelta


def create_wind_data(
    centroid,
    detection_time,
    hours_back=24,
    grid_size=1.0
):
    """
    Download wind data around a requested spill location
    and detection time.

    centroid:
        [longitude, latitude]

    detection_time:
        ISO timestamp, e.g.
        2026-09-01T20:45:15Z

    hours_back:
        Number of hours of historical wind data needed.

    grid_size:
        Size of the geographic area around the spill.
    """

    lon, lat = centroid

    # ============================================
    # GEOGRAPHIC GRID
    # ============================================

    lats = np.arange(
        lat - grid_size,
        lat + grid_size + 0.01,
        0.25
    )

    lons = np.arange(
        lon - grid_size,
        lon + grid_size + 0.01,
        0.25
    )

    # ============================================
    # TIME RANGE
    # ============================================

    detection_dt = datetime.fromisoformat(
        detection_time.replace("Z", "+00:00")
    )

    start_dt = detection_dt - timedelta(hours=hours_back)

    start_date = start_dt.strftime("%Y-%m-%d")
    end_date = (detection_dt + timedelta(days=1)).strftime("%Y-%m-%d")

    # ============================================
    # DOWNLOAD WIND DATA
    # ============================================

        # ============================================
    # DOWNLOAD WIND DATA
    # ============================================

    all_speed = []
    all_direction = []
    times = None

    for lat_point in lats:

        row_speed = []
        row_direction = []

        for lon_point in lons:

            url = (
                "https://archive-api.open-meteo.com/v1/archive"
                f"?latitude={lat_point}"
                f"&longitude={lon_point}"
                f"&start_date={start_date}"
                f"&end_date={end_date}"
                "&hourly=wind_speed_10m,wind_direction_10m"
                "&wind_speed_unit=ms"
                "&timezone=UTC"
            )

            response = requests.get(
                url,
                timeout=30
            )

            response.raise_for_status()

            data = response.json()

            if times is None:
                times = data["hourly"]["time"]

            row_speed.append(
                data["hourly"]["wind_speed_10m"]
            )

            row_direction.append(
                data["hourly"]["wind_direction_10m"]
            )

        all_speed.append(row_speed)
        all_direction.append(row_direction)

    if not all_speed or not all_direction:
        raise ValueError(
            "No wind data was downloaded."
        )

    # ============================================
    # TIME
    # ============================================

    times = data["hourly"]["time"]

    # Convert API timestamps to datetime objects
    api_times = [
        datetime.fromisoformat(t)
        for t in times
    ]
    window_start = start_dt.replace(tzinfo=None)

    window_end = (
        detection_dt + timedelta(hours=1)
    ).replace(tzinfo=None)

    selected_indices = [
        i
        for i, t in enumerate(api_times)
        if window_start <= t <= window_end
    ]

    if not selected_indices:
        raise ValueError(
            "No wind data found for requested time range."
        )

    times = [times[i] for i in selected_indices]

    speed = np.stack(
    [np.stack(row, axis=0) for row in all_speed],
    axis=0
)

    direction = np.stack(
    [np.stack(row, axis=0) for row in all_direction],
    axis=0
)

    speed = speed[:, :, selected_indices]
    direction = direction[:, :, selected_indices] 

    # ============================================
    # CONVERT SPEED + DIRECTION TO U/V
    # ============================================

    direction_rad = np.deg2rad(direction)

    # Meteorological direction = direction
    # wind comes FROM
    u_wind = -speed * np.sin(direction_rad)
    v_wind = -speed * np.cos(direction_rad)

    # Rearrange:
    # time, latitude, longitude

    u_wind = np.transpose(
        u_wind,
        (2, 0, 1)
    )

    v_wind = np.transpose(
        v_wind,
        (2, 0, 1)
    )

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
            "time": np.array(
                times,
                dtype="datetime64[ns]"
            ),
            "latitude": lats,
            "longitude": lons
        }
    )

    # ============================================
    # METADATA
    # ============================================

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

    ds.attrs["source"] = (
        "Open-Meteo historical weather API"
    )

    ds.attrs["description"] = (
        "10 metre wind components for OpenDrift"
    )

    # ============================================
    # SAVE
    # ============================================

    output_path = Path(
        "outputs/dynamic_wind.nc"
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    ds.to_netcdf(output_path)

    ds.close()

    print("========================================")
    print("DYNAMIC WIND DATA CREATED")
    print("========================================")
    print("Saved:", output_path)
    print(
        "Time:",
        times[0],
        "to",
        times[-1]
    )
    print(
        "Longitude:",
        lons.min(),
        "to",
        lons.max()
    )
    print(
        "Latitude:",
        lats.min(),
        "to",
        lats.max()
    )
    print("Variables:", ["x_wind", "y_wind"])
    print("========================================")

    return str(output_path)


if __name__ == "__main__":

    # Test using Team 1's actual sample
    test_centroid = [
        54.48877510459397,
        25.322134857980192
    ]

    test_detection_time = (
        "2026-09-01T20:45:15.466871Z"
    )

    create_wind_data(
        test_centroid,
        test_detection_time,
        hours_back=24
    )