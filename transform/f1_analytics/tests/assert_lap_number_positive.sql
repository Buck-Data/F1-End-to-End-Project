-- Rundennummern müssen >= 1 sein
SELECT *
FROM {{ ref('stg_laps') }}
WHERE lap_number < 1
