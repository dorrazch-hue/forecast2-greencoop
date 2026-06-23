with bergues as (
    select 'bergues' as station_key, * from {{ ref('stg_infoclimat__bergues') }}
),
hazebrouck as (
    select 'hazebrouck' as station_key, * from {{ ref('stg_infoclimat__hazebrouck') }}
),
armentieres as (
    select 'armentieres' as station_key, * from {{ ref('stg_infoclimat__armentieres') }}
),
lille_lesquin as (
    select 'lille_lesquin' as station_key, * from {{ ref('stg_infoclimat__lille_lesquin') }}
),
la_madeleine as (
    select
        'la_madeleine' as station_key,
        id_station, observed_at_utc, temperature_celsius,
        pressure_hpa, humidity_percent, dew_point_celsius,
        wind_speed_kmh, wind_gust_kmh,
        null::numeric as wind_direction_degrees,
        rain_1h_mm, null::numeric as rain_3h_mm,
        null::numeric as rain_24h_mm, uv_index,
        data_source, loaded_at
    from {{ ref('stg_wunderground__la_madeleine') }}
),
ichtegem as (
    select
        'ichtegem' as station_key,
        id_station, observed_at_utc, temperature_celsius,
        pressure_hpa, humidity_percent, dew_point_celsius,
        wind_speed_kmh, wind_gust_kmh,
        null::numeric as wind_direction_degrees,
        rain_1h_mm, null::numeric as rain_3h_mm,
        null::numeric as rain_24h_mm, uv_index,
        data_source, loaded_at
    from {{ ref('stg_wunderground__ichtegem') }}
),
unioned as (
    select * from bergues
    union all select * from hazebrouck
    union all select * from armentieres
    union all select * from lille_lesquin
    union all select * from la_madeleine
    union all select * from ichtegem
)
select * from unioned