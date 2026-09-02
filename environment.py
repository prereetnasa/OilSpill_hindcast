from pathlib import Path
import xarray as xr
from create_current_data import create_current_data
from create_wind_data import create_wind_data

CURRENT_FILE = Path("outputs/dynamic_currents.nc")
WIND_FILE = Path("outputs/dynamic_wind.nc")


def check_file_coverage(file_path, lon, lat):
    """
    Check whether a NetCDF file contains the requested
    longitude and latitude.
    """

    ds = xr.open_dataset(file_path)

    try:
        # Handle common longitude coordinate names
        if "longitude" in ds.coords:
            lon_values = ds["longitude"].values
        elif "lon" in ds.coords:
            lon_values = ds["lon"].values
        elif "loc" in ds.coords:
            lon_values = ds["loc"].values
        else:
            raise ValueError("Longitude coordinate not found.")

        # Handle common latitude coordinate names
        if "latitude" in ds.coords:
            lat_values = ds["latitude"].values
        elif "lat" in ds.coords:
            lat_values = ds["lat"].values
        else:
            raise ValueError("Latitude coordinate not found.")

        lon_min = float(lon_values.min())
        lon_max = float(lon_values.max())

        lat_min = float(lat_values.min())
        lat_max = float(lat_values.max())

        return (
            lon_min <= lon <= lon_max
            and
            lat_min <= lat <= lat_max
        )

    finally:
        ds.close()


def get_environment_files(centroid, detection_time):
    """
    Automatically create environmental data for
    the requested spill location and detection time.
    """

    print("========================================")
    print("PREPARING ENVIRONMENTAL DATA")
    print("========================================")

    print("Centroid:", centroid)
    print("Detection time:", detection_time)

    # ============================================
    # CREATE OCEAN CURRENT DATA
    # ============================================

    current_file = create_current_data(
        centroid,
        detection_time,
        hours_back=24,
        grid_size=1.0
    )

    # ============================================
    # CREATE WIND DATA
    # ============================================

    wind_file = create_wind_data(
        centroid,
        detection_time,
        hours_back=24,
        grid_size=1.0
    )

    # ============================================
    # CHECK FILES
    # ============================================

    if not Path(current_file).exists():
        raise FileNotFoundError(
            f"Current file was not created: {current_file}"
        )

    if not Path(wind_file).exists():
        raise FileNotFoundError(
            f"Wind file was not created: {wind_file}"
        )

    print("========================================")
    print("ENVIRONMENTAL DATA READY")
    print("========================================")
    print("Current:", current_file)
    print("Wind:", wind_file)
    print("========================================")

    return {
        "current": current_file,
        "wind": wind_file
    }