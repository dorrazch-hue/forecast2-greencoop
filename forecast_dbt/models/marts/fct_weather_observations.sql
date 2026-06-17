{{
    config(
        indexes=[
            {'columns': ['station_key'], 'type': 'btree'},
            {'columns': ['observed_at_utc'], 'type': 'btree'},
            {'columns': ['station_key', 'observed_at_utc'], 'type': 'btree'}
        ]
    )
}}

with observations as (

    select * from {{ ref('int_weather_observations_unioned') }}

),

stations as (

    select * from {{ ref('dim_weather_stations') }}

),

final as (

    select
        obs.station_key,
        stations.station_id,
        stations.station_name,
        obs.observed_at_utc,
        obs.temperature_celsius,
        obs.pressure_hpa,
        obs.humidity_percent,
        obs.dew_point_celsius,
        obs.wind_speed_kmh,
        obs.wind_gust_kmh,
        obs.wind_direction_degrees,
        obs.rain_1h_mm,
        obs.rain_3h_mm,
        obs.rain_24h_mm,
        obs.uv_index,
        obs.data_source,
        obs.loaded_at

    from observations as obs
    left join stations
        on obs.station_key = stations.station_key

)

select * from final