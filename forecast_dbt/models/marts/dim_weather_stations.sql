{{
    config(
        indexes=[
            {'columns': ['station_key'], 'type': 'btree', 'unique': True}
        ]
    )
}}

with stations as (

    select 'bergues' as station_key, '000R5' as station_id, 'Bergues' as station_name,
           50.968 as latitude, 2.441 as longitude, 17 as elevation_m,
           'France' as city, null as state, 'infoclimat' as network, 'StatIC' as hardware

    union all

    select 'hazebrouck' as station_key, 'STATIC0010' as station_id, 'Hazebrouck' as station_name,
           50.734 as latitude, 2.545 as longitude, 31 as elevation_m,
           'France' as city, null as state, 'infoclimat' as network, 'StatIC' as hardware

    union all

    select 'armentieres' as station_key, '00052' as station_id, 'Armentières' as station_name,
           50.689 as latitude, 2.877 as longitude, 16 as elevation_m,
           'France' as city, null as state, 'infoclimat' as network, 'StatIC' as hardware

    union all

    select 'la_madeleine' as station_key, 'ILAMAD25' as station_id, 'La Madeleine' as station_name,
           50.659 as latitude, 3.07 as longitude, 23 as elevation_m,
           'La Madeleine' as city, null as state, 'weather_underground' as network, 'EasyWeatherPro_V5.1.6' as hardware

    union all

    select 'ichtegem' as station_key, 'IICHTE19' as station_id, 'WeerstationBS' as station_name,
           51.092 as latitude, 2.999 as longitude, 15 as elevation_m,
           'Ichtegem' as city, null as state, 'weather_underground' as network, 'EasyWeatherV1.6.6' as hardware

)

select * from stations