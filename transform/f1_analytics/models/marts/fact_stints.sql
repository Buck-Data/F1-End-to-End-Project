SELECT
    s.session_key,
    s.meeting_key,
    s.driver_number,
    s.stint_number,
    s.lap_start,
    s.lap_end,
    s.lap_end - s.lap_start + 1 AS stint_laps,
    s.compound,
    s.tyre_age_at_start,
    d.name_acronym,
    d.full_name,
    d.team_name,
    d.team_colour,
    m.circuit_short_name,
    m.country_name,
    m.meeting_name
FROM {{ ref('stg_stints') }} s
LEFT JOIN {{ ref('stg_drivers') }} d
    ON s.session_key = d.session_key
    AND s.driver_number = d.driver_number
LEFT JOIN {{ ref('stg_meetings') }} m
    ON s.meeting_key = m.meeting_key