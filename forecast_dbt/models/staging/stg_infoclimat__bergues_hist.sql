with source as (

    select * from {{ source('raw_infoclimat', 'bergues_hist') }}

),

renamed as (

    select
        id_station,
        cast(dh_utc as timestamp) as observed_at_utc,
        cast(temperature as numeric) as temperature_celsius,
        cast(pression as numeric) as pressure_hpa,
        cast(humidite as numeric) as humidity_percent,
        cast(point_de_rosee as numeric) as dew_point_celsius,
        cast(vent_moyen as numeric) as wind_speed_kmh,
        cast(vent_rafales_10min as numeric) as wind_gust_kmh,
        cast(vent_direction as numeric) as wind_direction_degrees,
        cast(pluie_1h as numeric) as rain_1h_mm,
        cast(pluie_3h as numeric) as rain_3h_mm,
        cast(pluie_24h as numeric) as rain_24h_mm,
        cast(uv_index as numeric) as uv_index,
        source as data_source,
        current_timestamp as loaded_at

    from source

)

select * from renamed
