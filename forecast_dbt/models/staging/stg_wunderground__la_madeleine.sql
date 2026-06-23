with source as (

    select * from {{ source('raw_weather_underground', 'la_madeleine') }}

),

renamed as (

    select
        'ILAMAD25'                              as id_station,
        cast(observed_at as timestamp)          as observed_at_utc,
        cast(temperature_celsius as numeric)    as temperature_celsius,
        cast(dew_point_celsius as numeric)      as dew_point_celsius,
        cast(humidity_pct as numeric)           as humidity_percent,
        cast(wind_speed_kmh as numeric)         as wind_speed_kmh,
        cast(wind_gust_kmh as numeric)          as wind_gust_kmh,
        wind_direction                          as wind_direction_text,
        cast(pressure_hpa as numeric)           as pressure_hpa,
        cast(precip_rate_mm as numeric)         as rain_1h_mm,
        cast(precip_accum_mm as numeric)        as rain_accum_mm,
        cast(uv_index as numeric)               as uv_index,
        'weather_underground'                   as data_source,
        current_timestamp                       as loaded_at

    from source

)

select * from renamed