import pandas as pd
import matplotlib.pyplot as plt

RAW_PATH = "../data/laps_bahrain.csv"
CLEAN_PATH = "../data/laps_bahrain_clean.csv"
PLOT_PATH = "../data/degradation.png"

COMPOUND_COLORS = {"SOFT": "red", "MEDIUM": "gold", "HARD": "gray"}

# Column order must match the C# Lap class (LoadColumn 0..6)
FEATURES = ["Compound", "TyreLife", "LapNumber", "TrackTemp", "Team", "Year", "LapTimeSeconds"]

FUEL_EFFECT = 0.06 # approx. seconds per lap of fuel burned (assumption to test)

def log_step(df, step_name, previous_count):
    """Print how many laps a filter removed."""
    removed = previous_count - len(df)
    print(f"{step_name:<35} -{removed:>5}  → {len(df):>5} laps")
    return len(df)


def clean(df):
    count = len(df)
    print(f"{'Initial laps':<35} {'':>6}    {count:>5} laps")

    # 1. Laps without a recorded time
    df = df[df["LapTimeSeconds"].notna()]
    count = log_step(df, "1. Missing lap time", count)

    # 2. Lap 1: standing start and traffic, not representative
    df = df[df["LapNumber"] > 1]
    count = log_step(df, "2. First lap", count)

    # 3. Pit in / pit out laps: pit lane speed limit + stop time
    df = df[df["PitInTime"].isna() & df["PitOutTime"].isna()]
    count = log_step(df, "3. Pit in/out laps", count)

    # 4. Green flag only ("1" exactly; "12", "41"... mean the status changed mid-lap)
    df = df[df["TrackStatus"] == "1"]
    count = log_step(df, "4. Non-green track status", count)

    # 5. Laps FastF1 marks as accurate
    df = df[df["IsAccurate"] == True]
    count = log_step(df, "5. Inaccurate timing", count)

    # 6. Dry compounds only
    df = df[df["Compound"].isin(["SOFT", "MEDIUM", "HARD"])]
    count = log_step(df, "6. Non-dry compounds", count)

    # 7. Slow outliers: over 107% of the fastest lap of that race
    fastest_per_race = df.groupby("Year")["LapTimeSeconds"].transform("min")
    df = df[df["LapTimeSeconds"] <= fastest_per_race * 1.07]
    count = log_step(df, "7. Slower than 107% of fastest", count)

    return df


def plot_degradation(df):
    """Scatter of tyre age vs lap time, plus the median trend per compound."""
    max_lap = df.groupby("Year")["LapNumber"].transform("max")
    df = df.assign(LapTimeSeconds=df["LapTimeSeconds"] - (max_lap - df["LapNumber"]) * FUEL_EFFECT)
    
    fig, ax = plt.subplots(figsize=(11, 6))

    for compound, color in COMPOUND_COLORS.items():
        subset = df[df["Compound"] == compound]
        ax.scatter(subset["TyreLife"], subset["LapTimeSeconds"],
                   s=8, alpha=0.25, color=color)

        # The median per tyre age makes the trend visible through the noise
        median = subset.groupby("TyreLife")["LapTimeSeconds"].median()
        ax.plot(median.index, median.values, color=color, linewidth=2.5,
                label=f"{compound} (median)")

    ax.set_xlabel("Tyre life (laps)")
    ax.set_ylabel("Lap time (s)")
    ax.set_title("Bahrain 2022–2025 · Lap time vs tyre age (fuel-corrected)")
    ax.legend()
    ax.grid(alpha=0.3)

    fig.tight_layout()
    fig.savefig(PLOT_PATH, dpi=150)
    print(f"Plot saved to {PLOT_PATH}")
    plt.show()


def main():
    # TrackStatus as text so "1" and "12" stay different values
    df = pd.read_csv(RAW_PATH, dtype={"TrackStatus": str})
    
    TEAM_ALIASES = {
        "AlphaTauri": "Racing Bulls",
        "RB": "Racing Bulls",
        "Alfa Romeo": "Kick Sauber",
    }
    df["Team"] = df["Team"].replace(TEAM_ALIASES)

    df = clean(df)

    df = df[FEATURES]
    df.to_csv(CLEAN_PATH, index=False)
    print(f"\nSaved {len(df)} clean laps to {CLEAN_PATH} ✅")

    print("\nLaps per year:")
    print(df["Year"].value_counts().sort_index())

    plot_degradation(df)


if __name__ == "__main__":
    main()