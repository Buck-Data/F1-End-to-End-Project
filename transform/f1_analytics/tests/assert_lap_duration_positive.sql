-- Rundenzeiten müssen positiv sein
SELECT *
FROM {{ ref('stg_laps') }}
WHERE lap_duration <= 0
