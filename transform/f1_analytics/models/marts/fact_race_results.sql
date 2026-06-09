SELECT
    m.meeting_key,
    m.meeting_name,
    m.meeting_official_name,
    m.country_name,
    m.country_code,
    m.circuit_short_name,
    m.location,
    m.date_start        AS meeting_date,

    s.session_key,
    s.session_name,
    s.session_type,
    s.date_start        AS session_date,

    d.driver_number,
    d.full_name,
    d.name_acronym,
    d.team_name,
    d.team_colour,
    d.country_code      AS driver_country,

    l.lap_number,
    l.lap_time,
    l.duration_sector_1,
    l.duration_sector_2,
    l.duration_sector_3,
    l.st_speed,
    l.is_pit_out_lap

FROM {{ ref('stg_laps') }} l
LEFT JOIN {{ ref('stg_sessions') }} s
    ON l.session_key = s.session_key
LEFT JOIN {{ ref('stg_meetings') }} m
    ON s.meeting_key = m.meeting_key
LEFT JOIN {{ ref('stg_drivers') }} d
    ON l.session_key = d.session_key
    AND l.driver_number = d.driver_number