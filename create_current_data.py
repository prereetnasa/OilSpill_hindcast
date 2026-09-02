import subprocess
from pathlib import Path
from datetime import datetime, timedelta


def create_current_data(
    centroid,
    detection_time,
    hours_back=24,
    grid_size=1.0
):
    """
    Download Copernicus surface ocean-current data
    around a requested spill location and time.
    """

    lon, lat = centroid

    # Geographic area around spill
    minimum_longitude = lon - grid_size
    maximum_longitude = lon + grid_size

    minimum_latitude = lat - grid_size
    maximum_latitude = lat + grid_size

    # Time range
    detection_dt = datetime.fromisoformat(
        detection_time.replace("Z", "+00:00")
    )

    start_dt = detection_dt - timedelta(hours=hours_back)
    end_dt = detection_dt + timedelta(hours=1)

    # Output
    output_path = Path(
        "outputs/dynamic_currents.nc"
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # Copernicus dataset
    dataset_id = (
        "cmems_mod_glo_phy_anfc_merged-uv_PT1H-i"
    )

    command = [
        "copernicusmarine",
        "subset",

        "--dataset-id",
        dataset_id,

        "--variable",
        "uo",

        "--variable",
        "vo",

        "--minimum-longitude",
        str(minimum_longitude),

        "--maximum-longitude",
        str(maximum_longitude),

        "--minimum-latitude",
        str(minimum_latitude),

        "--maximum-latitude",
        str(maximum_latitude),

        "--start-datetime",
        start_dt.strftime("%Y-%m-%dT%H:%M:%S"),

        "--end-datetime",
        end_dt.strftime("%Y-%m-%dT%H:%M:%S"),

        "--output-directory",
        "outputs",

        "--output-filename",
        "dynamic_currents.nc"
    ]

    print("========================================")
    print("DOWNLOADING DYNAMIC OCEAN CURRENTS")
    print("========================================")

    print("Location:")
    print(
        minimum_longitude,
        "to",
        maximum_longitude
    )

    print(
        minimum_latitude,
        "to",
        maximum_latitude
    )

    print("Time:")
    print(start_dt.isoformat())
    print("to")
    print(end_dt.isoformat())

    print("Dataset:")
    print(dataset_id)

    print("========================================")

    subprocess.run(
        command,
        check=True
    )

    print("========================================")
    print("DYNAMIC CURRENT DATA CREATED")
    print("========================================")
    print("Saved:", output_path)
    print("========================================")

    return str(output_path)


if __name__ == "__main__":

    # Team 1 sample
    test_centroid = [
        54.48877510459397,
        25.322134857980192
    ]

    test_detection_time = (
        "2026-09-01T20:45:15.466871Z"
    )

    create_current_data(
        test_centroid,
        test_detection_time,
        hours_back=24
    )