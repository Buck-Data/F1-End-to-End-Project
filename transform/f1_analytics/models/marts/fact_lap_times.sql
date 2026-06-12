SELECT
    l.session_key,
    l.driver_number,
    l.lap_number,
    l.lap_duration,
    l.duration_sector_1,
    l.duration_sector_2,
    l.duration_sector_3,
    l.st_speed,
    l.is_pit_out_lap,
    d.full_name,
    d.name_acronym,
    d.team_name,
    d.team_colour,
    s.location,
    s.country_name,
    s.circuit_short_name,
    s.date_start
FROM {{ ref('stg_laps') }} l
LEFT JOIN {{ ref('stg_drivers') }} d
    ON l.session_key = d.session_key
    AND l.driver_number = d.driver_number
LEFT JOIN {{ ref('stg_sessions') }} s
    ON l.session_key = s.session_key