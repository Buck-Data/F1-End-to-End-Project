SELECT
    ct.session_key,
    ct.meeting_key,
    ct.team_name,
    ct.points_start,
    ct.points_current,
    ct.position_start,
    ct.position_current,

    m.meeting_name,
    m.circuit_short_name,
    m.country_name,
    m.date_start        AS meeting_date

FROM {{ ref('stg_championship_teams') }} ct
LEFT JOIN {{ ref('stg_meetings') }} m
    ON ct.meeting_key = m.meeting_key
