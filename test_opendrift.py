from datetime import datetime, timedelta
from opendrift.models.oceandrift import OceanDrift

print("Creating OpenDrift model...")

o = OceanDrift(loglevel=0)
o.set_config(
    'environment:fallback:x_sea_water_velocity',
    0.5
)

o.set_config(
    'environment:fallback:y_sea_water_velocity',
    0.0
)

lon = 74.81
lat = 12.51

o.seed_elements(
    lon=lon,
    lat=lat,
    number=1,
    time=datetime.now()
)

print("Particle seeded successfully!")

o.run(
    duration=timedelta(hours=1),
    time_step=-600
)
print("Simulation completed!")

final_lon = o.elements.lon[0]
final_lat = o.elements.lat[0]

print("Starting position:", lon, lat)
print("Final position:", float(final_lon), float(final_lat))