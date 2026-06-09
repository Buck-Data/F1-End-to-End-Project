-- Luftfeuchtigkeit muss zwischen 0 und 100 liegen
SELECT *
FROM {{ ref('stg_weather') }}
WHERE humidity < 0 OR humidity > 100
