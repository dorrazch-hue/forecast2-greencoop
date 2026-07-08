import json
import psycopg2
import os
from datetime import datetime

# Connexion PostgreSQL locale (Docker)
# Mot de passe local Docker - non secret, config de dev uniquement
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="forecast_db",
    user="forecast_user",
    password=os.environ.get("LOCAL_DB_PASSWORD", "forecast_pass")
)
cur = conn.cursor()

cur.execute("CREATE SCHEMA IF NOT EXISTS raw_infoclimat;")

for station_id in ["07015", "00052", "000R5", "STATIC0010"]:
    table = {
        "07015": "lille_lesquin",
        "00052": "armentieres",
        "000R5": "bergues_hist",
        "STATIC0010": "hazebrouck_hist"
    }[station_id]

    cur.execute(
        "CREATE TABLE IF NOT EXISTS raw_infoclimat." + table + " ("
        "id_station VARCHAR, dh_utc TIMESTAMP, temperature VARCHAR, "
        "pression VARCHAR, pression_variation_3h VARCHAR, humidite VARCHAR, "
        "point_de_rosee VARCHAR, visibilite VARCHAR, vent_moyen VARCHAR, "
        "vent_rafales VARCHAR, vent_rafales_10min VARCHAR, vent_direction VARCHAR, "
        "temperature_min VARCHAR, temperature_max VARCHAR, pluie_1h VARCHAR, "
        "pluie_3h VARCHAR, pluie_6h VARCHAR, pluie_12h VARCHAR, pluie_24h VARCHAR, "
        "pluie_cumul_0h VARCHAR, pluie_intensite VARCHAR, "
        "pluie_intensite_max_1h VARCHAR, uv VARCHAR, complements VARCHAR, "
        "ensoleillement VARCHAR, temperature_sol VARCHAR, temps_omm VARCHAR, "
        "source VARCHAR, uv_index VARCHAR, "
        "PRIMARY KEY (id_station, dh_utc)"
        ");"
    )

conn.commit()

# BUGFIX : ON CONFLICT DO NOTHING ne fonctionnait pas car les tables n'avaient
# aucune contrainte d'unicite -> chaque relance du script dupliquait les lignes.
# On ajoute la cle primaire (id_station, dh_utc), y compris sur les tables
# creees par d'anciennes executions du script.
for table in ["lille_lesquin", "armentieres", "bergues_hist", "hazebrouck_hist"]:
    try:
        cur.execute(
            "ALTER TABLE raw_infoclimat." + table +
            " ADD CONSTRAINT " + table + "_pkey PRIMARY KEY (id_station, dh_utc);"
        )
        conn.commit()
    except psycopg2.Error:
        conn.rollback()  # contrainte deja presente (ou doublons a nettoyer d'abord)

# Fichier JSON a placer dans forecast_meltano/data/
# Voir forecast_meltano/data/README.md pour les instructions
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
json_path = os.path.join(DATA_DIR, "data_source_infoclimat.json")

if not os.path.exists(json_path):
    print("Fichier JSON non trouve : " + json_path)
    print("-> Placez le fichier JSON dans forecast_meltano/data/data_source_infoclimat.json")
    cur.close()
    conn.close()
    exit(1)

with open(json_path, encoding="utf-8") as f:
    data = json.load(f)

station_map = {
    "07015": "lille_lesquin",
    "00052": "armentieres",
    "000R5": "bergues_hist",
    "STATIC0010": "hazebrouck_hist"
}

total = 0
for station_id, table in station_map.items():
    records = data["hourly"].get(station_id, [])
    if not records:
        print(station_id + ": 0 releves, ignore")
        continue

    for r in records:
        def s(k):
            v = r.get(k)
            return str(v) if v is not None else None

        cur.execute(
            "INSERT INTO raw_infoclimat." + table + " "
            "(id_station, dh_utc, temperature, pression, pression_variation_3h, "
            "humidite, point_de_rosee, visibilite, vent_moyen, vent_rafales, "
            "vent_rafales_10min, vent_direction, temperature_min, temperature_max, "
            "pluie_1h, pluie_3h, pluie_6h, pluie_12h, pluie_24h, pluie_cumul_0h, "
            "pluie_intensite, pluie_intensite_max_1h, uv, complements, "
            "ensoleillement, temperature_sol, temps_omm, source, uv_index) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) "
            "ON CONFLICT DO NOTHING;",
            (
                r.get("id_station"), r.get("dh_utc"),
                s("temperature"), s("pression"), s("pression_variation_3h"),
                s("humidite"), s("point_de_rosee"), s("visibilite"),
                s("vent_moyen"), s("vent_rafales"), s("vent_rafales_10min"),
                s("vent_direction"), s("temperature_min"), s("temperature_max"),
                s("pluie_1h"), s("pluie_3h"), s("pluie_6h"), s("pluie_12h"),
                s("pluie_24h"), s("pluie_cumul_0h"), s("pluie_intensite"),
                s("pluie_intensite_max_1h"), s("uv"), s("complements"),
                s("ensoleillement"), s("temperature_sol"), s("temps_omm"),
                s("source"), s("uv_index"),
            )
        )
    conn.commit()
    print(station_id + " (" + table + "): " + str(len(records)) + " releves charges")
    total += len(records)

print("Total: " + str(total) + " releves charges avec succes!")
cur.close()
conn.close()