with bergues as (
    select 'bergues' as station_key, * from {{ ref('stg_infoclimat__bergues') }}
),
-- CORRECTION : bergues_hist et hazebrouck_hist etaient declares dans _sources.yml
-- et charges/migres, mais absents de l'union -> donnees historiques perdues
-- dans les marts. On les ajoute (meme station_key que le flux Meltano),
-- puis on deduplique sur (station_key, observed_at_utc) en cas de recouvrement.
bergues_hist as (
    select 'bergues' as station_key, * from {{ ref('stg_infoclimat__bergues_hist') }}
),
hazebrouck as (
    select 'hazebrouck' as station_key, * from {{ ref('stg_infoclimat__hazebrouck') }}
),
hazebrouck_hist as (
    select 'hazebrouck' as station_key, * from {{ ref('stg_infoclimat__hazebrouck_hist') }}
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
    union all select * from bergues_hist
    union all select * from hazebrouck
    union all select * from hazebrouck_hist
    union all select * from armentieres
    union all select * from lille_lesquin
    union all select * from la_madeleine
    union all select * from ichtegem
),
deduplicated as (
    select *
    from (
        select
            *,
            row_number() over (
                partition by station_key, observed_at_utc
                order by loaded_at desc
            ) as rn
        from unioned
    ) ranked
    where rn = 1
)
select
    station_key, id_station, observed_at_utc, temperature_celsius,
    pressure_hpa, humidity_percent, dew_point_celsius,
    wind_speed_kmh, wind_gust_kmh, wind_direction_degrees,
    rain_1h_mm, rain_3h_mm, rain_24h_mm, uv_index,
    data_source, loaded_at
from deduplicated