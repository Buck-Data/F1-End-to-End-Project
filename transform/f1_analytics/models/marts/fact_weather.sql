SELECT
    w.session_key,
    w.date,
    w.air_temperature,
    w.track_temperature,
    w.humidity,
    w.pressure,
    w.wind_speed,
    w.wind_direction,
    w.rainfall,

    s.session_name,
    s.session_type,
    s.meeting_key,

    m.meeting_name,
    m.circuit_short_name,
    m.country_name

FROM {{ ref('stg_weather') }} w
LEFT JOIN {{ ref('stg_sessions') }} s
    ON w.session_key = s.session_key
LEFT JOIN {{ ref('stg_meetings') }} m
    ON s.meeting_key = m.meeting_key