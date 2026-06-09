-- Jede Kombination session_key + driver_number + lap_number muss eindeutig sein
SELECT session_key, driver_number, lap_number, COUNT(*) AS cnt
FROM {{ ref('stg_laps') }}
GROUP BY session_key, driver_number, lap_number
HAVING COUNT(*) > 1
