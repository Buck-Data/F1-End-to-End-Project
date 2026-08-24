SELECT DISTINCT
    session_key,
    driver_number,
    lap_number,
    lap_duration,
    duration_sector_1,
    duration_sector_2,
    duration_sector_3,
    st_speed,
    is_pit_out_lap
FROM raw.laps
WHERE lap_duration IS NOT NULL