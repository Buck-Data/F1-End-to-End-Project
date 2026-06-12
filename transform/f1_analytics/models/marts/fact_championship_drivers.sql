SELECT
    cd.session_key,
    cd.meeting_key,
    cd.driver_number,
    cd.points_start,
    cd.points_current,
    cd.position_start,
    cd.position_current,

    d.full_name,
    d.name_acronym,
    d.team_name,
    d.team_colour,
    d.country_code      AS driver_country,
    d.image_url,
    d.teamshot_url,

    m.meeting_name,
    m.circuit_short_name,
    m.country_name,
    m.date_start        AS meeting_date

FROM {{ ref('stg_championship_drivers') }} cd
LEFT JOIN {{ ref('stg_drivers') }} d
    ON cd.session_key = d.session_key
    AND cd.driver_number = d.driver_number
LEFT JOIN {{ ref('stg_meetings') }} m
    ON cd.meeting_key = m.meeting_key
