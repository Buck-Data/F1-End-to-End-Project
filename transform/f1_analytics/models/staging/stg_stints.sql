SELECT
    session_key,
    meeting_key,
    driver_number,
    stint_number,
    lap_start,
    lap_end,
    COALESCE(compound, 'UNKNOWN') AS compound,
    tyre_age_at_start
FROM raw.stints
WHERE session_key IS NOT NULL
