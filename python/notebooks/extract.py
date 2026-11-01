import os
import fastf1
import pandas as pd

YEARS = [2022, 2023, 2024, 2025]
CIRCUIT = "Bahrain"

def load_race(year, circuit):
    session = fastf1.get_session(year, circuit, "R")
    session.load(telemetry=False, messages=False) # we don't need telemetry: much faster
    
    laps = session.laps
    weather = laps.get_weather_data().reset_index(drop=True)
    laps = laps.reset_index(drop=True)
    
    # Match the weather data: same number of rows and same order as the time intervals (laps)
    laps["TrackTemp"] = weather["TrackTemp"]
    laps["AirTemp"] = weather["AirTemp"]
    laps["Rainfall"] = weather["Rainfall"]
    
    # Knowing which year each lap belongs to (in order to separate train/test sets later)
    laps["Year"] = year
    
    # timedelta → seconds (float), which is what ML.NET understands
    laps["LapTimeSeconds"] = laps["LapTime"].dt.total_seconds()
    
    return laps

def main():
    os.makedirs("cache", exist_ok=True)
    fastf1.Cache.enable_cache("cache")
    
    all_laps = []
    for year in YEARS:
        print(f"Loading {year}...")
        laps = load_race(year, CIRCUIT) # ← inside the for loop (4 additional spaces)
        all_laps.append(laps) # ← inside the for loop
        print(f" {len(laps)} laps") # ← inside the for loop
        
    df = pd.concat(all_laps, ignore_index=True)
    
    columns = ["Driver", "Team", "Year", "LapNumber", "LapTimeSeconds",
                "Compound", "TyreLife", "Stint", "PitInTime", "PitOutTime",
                "TrackStatus", "IsAccurate", "TrackTemp", "AirTemp", "Rainfall"]
    
    os.makedirs("../data", exist_ok=True)
    df[columns].to_csv("../data/laps_bahrain.csv", index=False)
    print(f"Saved: {len(df)} total number of laps")

if __name__ == "__main__":
    main()