-- ============================================================
-- Capital Bikeshare Data Warehouse
-- CREATE TABLE Scripts
-- ============================================================

-- 1. DIMENSION: Date
CREATE TABLE dim_date (
    date_id       SERIAL PRIMARY KEY,
    start_date    DATE        NOT NULL,
    start_year    INTEGER     NOT NULL,
    start_month   INTEGER     NOT NULL,
    start_day     INTEGER     NOT NULL,
    start_hour    INTEGER     NOT NULL
);

-- 2. DIMENSION: Station
CREATE TABLE dim_station (
    station_id        SERIAL PRIMARY KEY,
    station_name      VARCHAR(100),
    station_code      VARCHAR(50),
    lat               FLOAT,
    lng               FLOAT
);

-- 3. DIMENSION: User
CREATE TABLE dim_user (
    user_id       SERIAL PRIMARY KEY,
    member_type   VARCHAR(10) NOT NULL
);

-- 4. FACT: Trips
CREATE TABLE fact_trips (
    trip_id             SERIAL PRIMARY KEY,
    ride_id             VARCHAR(50)     NOT NULL,
    rideable_type       VARCHAR(20),
    started_at          TIMESTAMP       NOT NULL,
    ended_at            TIMESTAMP       NOT NULL,
    trip_duration_mins  FLOAT,
    start_date          DATE,
    date_id             INTEGER         REFERENCES dim_date(date_id),
    start_station_id    INTEGER         REFERENCES dim_station(station_id),
    end_station_id      INTEGER         REFERENCES dim_station(station_id),
    user_id             INTEGER         REFERENCES dim_user(user_id),
    ingestion_date      DATE,
    source_file         VARCHAR(100)
);