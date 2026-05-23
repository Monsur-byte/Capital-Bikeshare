import os
import pandas as pd
from datetime import datetime

# ── CONFIG ────────────────────────────────────────────────────────────────────
# Path to the folder where you saved your CSV(s)
DATA_FOLDER = "."  # current directory (run this script from inside CapitalBikeShareData)
# ──────────────────────────────────────────────────────────────────────────────


def load_all_csvs(folder: str) -> pd.DataFrame:
    """Read all CSV files in the folder and combine them into one DataFrame."""
    all_frames = []

    csv_files = [f for f in os.listdir(folder) if f.endswith(".csv")]

    if not csv_files:
        print("[ERROR] No CSV files found in folder:", folder)
        return pd.DataFrame()

    for filename in csv_files:
        filepath = os.path.join(folder, filename)
        print(f"[READ]  {filepath}")
        df = pd.read_csv(filepath)

        # Add ingestion metadata
        df["ingestion_date"] = datetime.today().strftime("%Y-%m-%d")
        df["source_file"]    = filename

        print(f"[INFO]  Loaded {len(df):,} rows from {filename}\n")
        all_frames.append(df)

    combined = pd.concat(all_frames, ignore_index=True)
    return combined


def main():
    print(f"[INFO]  Looking for CSVs in: {DATA_FOLDER}\n")
    df = load_all_csvs(DATA_FOLDER)

    if df.empty:
        return

    print(f"[INFO]  Total rows: {len(df):,}")
    print(f"[INFO]  Columns: {list(df.columns)}\n")
    print(df.head())

    # Save combined output
    output_path = os.path.join(DATA_FOLDER, "combined_raw.csv")
    df.to_csv(output_path, index=False)
    print(f"\n[SAVED] Combined data → {output_path}")

    return df


if __name__ == "__main__":
    main()
