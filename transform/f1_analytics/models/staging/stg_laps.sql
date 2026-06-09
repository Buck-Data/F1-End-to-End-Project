SELECT
    session_key,
    driver_number,
    lap_number,
    printf('%d:%02d.%03d',
           FLOOR(lap_duration / 60)::INT,
           (FLOOR(lap_duration) % 60)::INT,
           ROUND((lap_duration - FLOOR(lap_duration)) * 1000)::INT
           ) AS lap_time,
    duration_sector_1,
    duration_sector_2,
    duration_sector_3,
    st_speed,
    is_pit_out_lap
FROM raw.laps
WHERE lap_duration IS NOT NULL