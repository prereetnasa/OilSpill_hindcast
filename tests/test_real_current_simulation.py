from datetime import timedelta

from opendrift.models.oceandrift import OceanDrift
from opendrift.readers import reader_netCDF_CF_generic


print("Loading Indian Ocean currents...")

reader = reader_netCDF_CF_generic.Reader(
    "outputs/indian_ocean_currents.nc"
)

print("Reader loaded!")
print("Start time:", reader.start_time)
print("End time:", reader.end_time)
print("Variables:", reader.variables)

o = OceanDrift(loglevel=0)

o.add_reader(reader)

lon = 74.81
lat = 12.51

print("Seeding particle...")

o.seed_elements(
    lon=lon,
    lat=lat,
    number=1,
    time=reader.start_time
)

print("Running simulation...")

o.run(
    duration=timedelta(hours=1),
    time_step=600,
    time_step_output=600
)

print("Simulation completed!")

print("Starting position:", lon, lat)
print("Final longitude:", float(o.elements.lon[0]))
print("Final latitude:", float(o.elements.lat[0]))