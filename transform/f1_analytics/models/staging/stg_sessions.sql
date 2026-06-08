SELECT
    session_key,
    session_name,
    session_type,
    meeting_key,
    location,
    country_name,
    circuit_short_name,
    date_start,
    gmt_offset,
    is_cancelled
FROM raw.sessions
WHERE is_cancelled = false