SELECT
    d.session_key,
    d.driver_number,
    d.full_name,
    d.name_acronym,
    d.first_name,
    d.last_name,
    d.team_name,
    d.team_colour,
    d.country_code,
    d.meeting_key,
    i.image_url,
    i.teamshot_url
FROM raw.drivers d
INNER JOIN {{ ref('stg_sessions') }} s
    ON d.session_key = s.session_key
LEFT JOIN {{ ref('driver_images') }} i
    ON d.driver_number = i.driver_number
