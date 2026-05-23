import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime

# ── CONFIG ────────────────────────────────────────────────────────────────────
CSV_PATH = "combined_raw.csv"  # output from sourcing.py

DB_CONFIG = {
    "host":     "db.wbyqaaydrcqwqmpqdwvg.supabase.co",
    "port":     5432,
    "dbname":   "postgres",
    "user":     "postgres",
    "password": "Butterflies123#shuna"
}
# ──────────────────────────────────────────────────────────────────────────────


# ── STEP 1: LOAD RAW DATA ─────────────────────────────────────────────────────
def load_data(path):
    print(f"[LOAD] Reading {path}...")
    df = pd.read_csv(path)
    print(f"[INFO] Loaded {len(df):,} rows\n")
    return df


# ── STEP 2: TRANSFORM ─────────────────────────────────────────────────────────
def transform(df):
    print("[TRANSFORM] Cleaning data...")

    # Drop duplicates
    before = len(df)
    df = df.drop_duplicates(subset="ride_id")
    print(f"  Removed {before - len(df):,} duplicate rows")

    # Drop rows missing critical fields
    df = df.dropna(subset=["ride_id", "started_at", "ended_at", "member_casual"])
    print(f"  Rows after dropping nulls: {len(df):,}")

    # Standardize date format to YYYY-MM-DD HH:MM:SS
    df["started_at"] = pd.to_datetime(df["started_at"]).dt.strftime("%Y-%m-%d %H:%M:%S")
    df["ended_at"]   = pd.to_datetime(df["ended_at"]).dt.strftime("%Y-%m-%d %H:%M:%S")

    # Extract date parts
    started = pd.to_datetime(df["started_at"])
    df["start_date"]  = started.dt.strftime("%Y-%m-%d")
    df["start_year"]  = started.dt.year
    df["start_month"] = started.dt.month
    df["start_day"]   = started.dt.day
    df["start_hour"]  = started.dt.hour

    # Calculate trip duration in minutes
    df["trip_duration_mins"] = (
        (pd.to_datetime(df["ended_at"]) - pd.to_datetime(df["started_at"]))
        .dt.total_seconds() / 60
    ).round(2)

    # Remove trips with negative or zero duration
    df = df[df["trip_duration_mins"] > 0]
    print(f"  Rows after removing invalid durations: {len(df):,}")

    # Fix data types
    df["start_year"]  = df["start_year"].astype(int)
    df["start_month"] = df["start_month"].astype(int)
    df["start_day"]   = df["start_day"].astype(int)
    df["start_hour"]  = df["start_hour"].astype(int)

    print(f"[INFO] Transformation complete. Final row count: {len(df):,}\n")
    return df


# ── STEP 3: LOAD INTO DATABASE ────────────────────────────────────────────────
def load_to_db(df):
    print("[LOAD] Connecting to database...")
    conn = psycopg2.connect(**DB_CONFIG)
    cur  = conn.cursor()
    print("[INFO] Connected!\n")

    # -- dim_user ---------------------------------------------------------------
    print("[LOAD] Inserting dim_user...")
    user_types = df["member_casual"].unique()
    user_map   = {}
    for ut in user_types:
        cur.execute(
            "INSERT INTO dim_user (member_type) VALUES (%s) ON CONFLICT DO NOTHING RETURNING user_id",
            (ut,)
        )
        row = cur.fetchone()
        if row:
            user_map[ut] = row[0]
        else:
            cur.execute("SELECT user_id FROM dim_user WHERE member_type = %s", (ut,))
            user_map[ut] = cur.fetchone()[0]
    print(f"  Inserted {len(user_map)} user types\n")

    # -- dim_station ------------------------------------------------------------
    print("[LOAD] Inserting dim_station...")
    stations = pd.concat([
        df[["start_station_name", "start_station_id", "start_lat", "start_lng"]]
          .rename(columns={"start_station_name": "name", "start_station_id": "code",
                           "start_lat": "lat", "start_lng": "lng"}),
        df[["end_station_name", "end_station_id", "end_lat", "end_lng"]]
          .rename(columns={"end_station_name": "name", "end_station_id": "code",
                           "end_lat": "lat", "end_lng": "lng"})
    ]).drop_duplicates(subset="code").dropna(subset=["code"])

    station_map = {}
    for _, row in stations.iterrows():
        cur.execute("""
            INSERT INTO dim_station (station_name, station_code, lat, lng)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT DO NOTHING RETURNING station_id
        """, (row["name"], str(row["code"]), row.get("lat"), row.get("lng")))
        result = cur.fetchone()
        if result:
            station_map[str(row["code"])] = result[0]
        else:
            cur.execute("SELECT station_id FROM dim_station WHERE station_code = %s", (str(row["code"]),))
            station_map[str(row["code"])] = cur.fetchone()[0]
    print(f"  Inserted {len(station_map)} stations\n")

    # -- dim_date ---------------------------------------------------------------
    print("[LOAD] Inserting dim_date...")
    dates = df[["start_date", "start_year", "start_month", "start_day", "start_hour"]].drop_duplicates()
    date_map = {}
    for _, row in dates.iterrows():
        cur.execute("""
            INSERT INTO dim_date (start_date, start_year, start_month, start_day, start_hour)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING RETURNING date_id
        """, (row["start_date"], int(row["start_year"]), int(row["start_month"]),
              int(row["start_day"]), int(row["start_hour"])))
        result = cur.fetchone()
        key = (row["start_date"], int(row["start_hour"]))
        if result:
            date_map[key] = result[0]
        else:
            cur.execute("""
                SELECT date_id FROM dim_date
                WHERE start_date = %s AND start_hour = %s
            """, (row["start_date"], int(row["start_hour"])))
            date_map[key] = cur.fetchone()[0]
    print(f"  Inserted {len(date_map)} date records\n")

    # -- fact_trips -------------------------------------------------------------
    print("[LOAD] Inserting fact_trips (this may take a few minutes)...")
    records = []
    for _, row in df.iterrows():
        date_key    = (row["start_date"], int(row["start_hour"]))
        start_st_id = station_map.get(str(row.get("start_station_id")))
        end_st_id   = station_map.get(str(row.get("end_station_id")))
        user_id     = user_map.get(row["member_casual"])
        date_id     = date_map.get(date_key)

        records.append((
            row["ride_id"],
            row["rideable_type"],
            row["started_at"],
            row["ended_at"],
            row["trip_duration_mins"],
            row["start_date"],
            date_id,
            start_st_id,
            end_st_id,
            user_id,
            row["ingestion_date"],
            row["source_file"]
        ))

    execute_values(cur, """
        INSERT INTO fact_trips (
            ride_id, rideable_type, started_at, ended_at,
            trip_duration_mins, start_date, date_id,
            start_station_id, end_station_id, user_id,
            ingestion_date, source_file
        ) VALUES %s
    """, records, page_size=1000)

    conn.commit()
    cur.close()
    conn.close()
    print(f"  Inserted {len(records):,} trip records\n")
    print("[DONE] All data loaded successfully!")


# ── MAIN ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    df = load_data(CSV_PATH)
    df = transform(df)
    load_to_db(df)
