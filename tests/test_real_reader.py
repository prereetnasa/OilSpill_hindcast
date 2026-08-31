from opendrift.readers import reader_netCDF_CF_generic

print("Loading real ocean current data...")

reader = reader_netCDF_CF_generic.Reader(
    "https://thredds.met.no/thredds/dodsC/fou-hi/norkystv3_800m_m00_be"
)

print("Reader created successfully!")
print("Start time:", reader.start_time)
print("End time:", reader.end_time)
print("Variables:", reader.variables)
print("Reader longitude range:", reader.xmin, "to", reader.xmax)
print("Reader latitude range:", reader.ymin, "to", reader.ymax)
print("Reader variables:", reader.variables)