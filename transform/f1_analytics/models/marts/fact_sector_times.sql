SELECT
    session_key,
    driver_number,
    lap_number,
    'S1' AS sector,
    duration_sector_1 AS sector_time
FROM {{ ref('stg_laps') }}
WHERE duration_sector_1 > 0

UNION ALL

SELECT
    session_key,
    driver_number,
    lap_number,
    'S2' AS sector,
    duration_sector_2 AS sector_time
FROM {{ ref('stg_laps') }}
WHERE duration_sector_2 > 0

UNION ALL

SELECT
    session_key,
    driver_number,
    lap_number,
    'S3' AS sector,
    duration_sector_3 AS sector_time
FROM {{ ref('stg_laps') }}
WHERE duration_sector_3 > 0
