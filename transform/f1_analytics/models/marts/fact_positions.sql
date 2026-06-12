SELECT
    p.session_key,
    p.meeting_key,
    p.driver_number,
    p.date,
    p.position

FROM {{ ref('stg_positions') }} p
