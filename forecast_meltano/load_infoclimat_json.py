import json
import psycopg2
from datetime import datetime

# Connexion PostgreSQL
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="forecast_db",
    user="forecast_user",
    password="forecast_pass"
)
cur = conn.cursor()

# Création du schéma et des tables si nécessaire
cur.execute("CREATE SCHEMA IF NOT EXISTS raw_infoclimat;")

for station_id in ['07015', '00052', '000R5', 'STATIC0010']:
    table = {
        '07015': 'lille_lesquin',
        '00052': 'armentieres',
        '000R5': 'bergues_hist',
        'STATIC0010': 'hazebrouck_hist'
    }[station_id]

    cur.execute(f"""
        CREATE TABLE IF NOT EXISTS raw_infoclimat.{table} (
            id_station VARCHAR,
            dh_utc TIMESTAMP,
            temperature VARCHAR,
            pression VARCHAR,
            pression_variation_3h VARCHAR,
            humidite VARCHAR,
            point_de_rosee VARCHAR,
            visibilite VARCHAR,
            vent_moyen VARCHAR,
            vent_rafales VARCHAR,
            vent_rafales_10min VARCHAR,
            vent_direction VARCHAR,
            temperature_min VARCHAR,
            temperature_max VARCHAR,
            pluie_1h VARCHAR,
            pluie_3h VARCHAR,
            pluie_6h VARCHAR,
            pluie_12h VARCHAR,
            pluie_24h VARCHAR,
            pluie_cumul_0h VARCHAR,
            pluie_intensite VARCHAR,
            pluie_intensite_max_1h VARCHAR,
            uv VARCHAR,
            complements VARCHAR,
            ensoleillement VARCHAR,
            temperature_sol VARCHAR,
            temps_omm VARCHAR,
            source VARCHAR,
            uv_index VARCHAR
        );
    """)

conn.commit()

# Chargement des données
with open('data_source1.json', encoding='utf-8') as f:
    data = json.load(f)

station_map = {
    '07015': 'lille_lesquin',
    '00052': 'armentieres',
    '000R5': 'bergues_hist',
    'STATIC0010': 'hazebrouck_hist'
}

total = 0
for station_id, table in station_map.items():
    records = data['hourly'].get(station_id, [])
    if not records:
        print(f"{station_id}: 0 relevés, ignoré")
        continue

    for r in records:
        cur.execute(f"""
            INSERT INTO raw_infoclimat.{table}
            (id_station, dh_utc, temperature, pression, pression_variation_3h,
             humidite, point_de_rosee, visibilite, vent_moyen, vent_rafales,
             vent_rafales_10min, vent_direction, temperature_min, temperature_max,
             pluie_1h, pluie_3h, pluie_6h, pluie_12h, pluie_24h, pluie_cumul_0h,
             pluie_intensite, pluie_intensite_max_1h, uv, complements,
             ensoleillement, temperature_sol, temps_omm, source, uv_index)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT DO NOTHING;
        """, (
            r.get('id_station'), r.get('dh_utc'), str(r.get('temperature')) if r.get('temperature') is not None else None,
            str(r.get('pression')) if r.get('pression') is not None else None,
            str(r.get('pression_variation_3h')) if r.get('pression_variation_3h') is not None else None,
            str(r.get('humidite')) if r.get('humidite') is not None else None,
            str(r.get('point_de_rosee')) if r.get('point_de_rosee') is not None else None,
            str(r.get('visibilite')) if r.get('visibilite') is not None else None,
            str(r.get('vent_moyen')) if r.get('vent_moyen') is not None else None,
            str(r.get('vent_rafales')) if r.get('vent_rafales') is not None else None,
            str(r.get('vent_rafales_10min')) if r.get('vent_rafales_10min') is not None else None,
            str(r.get('vent_direction')) if r.get('vent_direction') is not None else None,
            str(r.get('temperature_min')) if r.get('temperature_min') is not None else None,
            str(r.get('temperature_max')) if r.get('temperature_max') is not None else None,
            str(r.get('pluie_1h')) if r.get('pluie_1h') is not None else None,
            str(r.get('pluie_3h')) if r.get('pluie_3h') is not None else None,
            str(r.get('pluie_6h')) if r.get('pluie_6h') is not None else None,
            str(r.get('pluie_12h')) if r.get('pluie_12h') is not None else None,
            str(r.get('pluie_24h')) if r.get('pluie_24h') is not None else None,
            str(r.get('pluie_cumul_0h')) if r.get('pluie_cumul_0h') is not None else None,
            str(r.get('pluie_intensite')) if r.get('pluie_intensite') is not None else None,
            str(r.get('pluie_intensite_max_1h')) if r.get('pluie_intensite_max_1h') is not None else None,
            str(r.get('uv')) if r.get('uv') is not None else None,
            str(r.get('complements')) if r.get('complements') is not None else None,
            str(r.get('ensoleillement')) if r.get('ensoleillement') is not None else None,
            str(r.get('temperature_sol')) if r.get('temperature_sol') is not None else None,
            str(r.get('temps_omm')) if r.get('temps_omm') is not None else None,
            str(r.get('source')) if r.get('source') is not None else None,
            str(r.get('uv_index')) if r.get('uv_index') is not None else None,
        ))
    conn.commit()
    print(f"{station_id} ({table}): {len(records)} relevés chargés")
    total += len(records)

print(f"\nTotal: {total} relevés chargés avec succès !")
cur.close()
conn.close()