import os
import fastf1
import pandas as pd

pd.set_option("display.max_columns", None) # show every column
pd.set_option("display.width", 200)

os.makedirs("cache", exist_ok=True)
fastf1.Cache.enable_cache("cache")

session = fastf1.get_session(2024, "Bahrain", "R")
session.load()
laps = session.laps

# 1. Columns and types
print(laps.dtypes)

# 2. Laps per driver
print(laps["Driver"].value_counts())

# 3. Compounds used
print(laps["Compound"].value_counts())

# 4. Verstappen's stints
ver = laps[laps["Driver"] == "VER"]
print(ver[["LapNumber", "Stint", "Compound", "TyreLife", "LapTime"]])

# 5. Pit in / pit out laps
pit_laps = laps[laps["PitInTime"].notna() | laps["PitOutTime"].notna()]
print(pit_laps[["Driver", "LapNumber", "LapTime", "PitInTime", "PitOutTime"]].head(10))

# 6. Weather per lap
weather = laps.get_weather_data()
print(weather["TrackTemp"].describe())
