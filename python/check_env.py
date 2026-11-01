import os        # built-in module for files and folders
import fastf1    # the F1 data library

def main():
    # 1. Make sure the cache folder exists (FastF1 errors if it doesn't)
    os.makedirs("cache", exist_ok=True)

    # 2. Tell FastF1 to save downloads there, so the next run is instant
    fastf1.Cache.enable_cache("cache")

    # 3. Pick a session: year, Grand Prix, and session type ('R' = race)
    session = fastf1.get_session(2024, "Bahrain", "R")

    # 4. Download and process the data (slow the first time)
    session.load()

    # 5. session.laps is a pandas DataFrame: one row per lap per driver
    laps = session.laps

    # 6. Keep only the columns we care about and show the first 10 rows
    columns = ["Driver", "LapNumber", "LapTime", "Compound", "TyreLife"]
    print(laps[columns].head(10))

    # 7. A quick sanity check: how many laps did we get?
    print(f"\nTotal laps loaded: {len(laps)}")

# This makes main() run only when you execute the file directly
if __name__ == "__main__":
    main()