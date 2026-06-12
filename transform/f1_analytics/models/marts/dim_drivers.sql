SELECT
    DISTINCT ON (driver_number)
    driver_number,
    session_key,
    full_name,
    name_acronym,
    team_name,
    team_colour,
    country_code,
    meeting_key,
    image_url,
    teamshot_url
FROM {{ ref('stg_drivers') }}
ORDER BY driver_number, session_key DESC