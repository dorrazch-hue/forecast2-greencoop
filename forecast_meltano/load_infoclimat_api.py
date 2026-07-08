# -*- coding: utf-8 -*-
"""
Script de secours : ingestion InfoClimat sans Meltano.

Pourquoi ce script existe :
- Le pipeline principal est Meltano (voir meltano.yml). Sur certains postes,
  la politique de securite Windows "Smart App Control" bloque les executables
  non signes installes par pip (erreur WinError 4551), ce qui empeche Meltano
  de lancer ses plugins.
- Ce script appelle LA MEME API InfoClimat, avec LES MEMES dates (.env),
  et ecrit dans LES MEMES tables (raw_infoclimat.bergues / hazebrouck),
  avec la meme cle de deduplication (dh_utc). DBT ne voit aucune difference.

Utilisation :
    python load_infoclimat_api.py
Les dates et le token sont lus dans le fichier .env :
    TAP_INFOCLIMAT_TOKEN=...
    INFOCLIMAT_START=2026-07-01
    INFOCLIMAT_END=2026-07-08
"""

import json
import os
import urllib.parse
import urllib.request
from datetime import datetime, timezone

import psycopg2

# ---------------------------------------------------------------- .env
ENV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")

def load_env(path):
    values = {}
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, val = line.partition("=")
                    values[key.strip()] = val.strip()
    return values

env = load_env(ENV_PATH)
TOKEN = env.get("TAP_INFOCLIMAT_TOKEN") or os.environ.get("TAP_INFOCLIMAT_TOKEN")
START = env.get("INFOCLIMAT_START") or os.environ.get("INFOCLIMAT_START")
END = env.get("INFOCLIMAT_END") or os.environ.get("INFOCLIMAT_END")

if not TOKEN or not START or not END:
    raise SystemExit(
        "Il manque TAP_INFOCLIMAT_TOKEN, INFOCLIMAT_START ou INFOCLIMAT_END "
        "dans forecast_meltano/.env"
    )

# ------------------------------------------------- stations et colonnes
# Memes stations que meltano.yml, memes tables cibles.
STATIONS = {
    "bergues": "000R5",
    "hazebrouck": "STATIC0010",
}

# Memes colonnes que schemas/bergues.json et schemas/hazebrouck.json
COLUMNS = [
    "id_station", "dh_utc", "temperature", "pression", "pression_variation_3h",
    "humidite", "point_de_rosee", "visibilite", "vent_moyen", "vent_rafales",
    "vent_rafales_10min", "vent_direction", "temperature_min", "temperature_max",
    "pluie_1h", "pluie_3h", "pluie_6h", "pluie_12h", "pluie_24h",
    "pluie_cumul_0h", "pluie_intensite", "pluie_intensite_max_1h", "uv",
    "complements", "ensoleillement", "temperature_sol", "temps_omm",
    "source", "uv_index",
]

API_URL = "https://www.infoclimat.fr/opendata/"

def fetch_station(code):
    params = urllib.parse.urlencode({
        "version": "2",
        "method": "get",
        "format": "json",
        "token": TOKEN,
        "start": START,
        "end": END,
        "stations[]": code,
    })
    with urllib.request.urlopen(API_URL + "?" + params, timeout=60) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data.get("hourly", {}).get(code, []) or []

# ---------------------------------------------------------------- base
conn = psycopg2.connect(
    host="localhost", port=5432,
    database="forecast_db", user="forecast_user", password="forecast_pass",
)
cur = conn.cursor()

total = 0
for table, code in STATIONS.items():
    records = fetch_station(code)
    inserted = 0
    now_utc = datetime.now(timezone.utc)
    for rec in records:
        if not isinstance(rec, dict) or not rec.get("dh_utc"):
            continue
        values = [None if rec.get(c) is None else str(rec.get(c)) for c in COLUMNS]
        placeholders = ", ".join(["%s"] * (len(COLUMNS) + 1))
        cur.execute(
            "INSERT INTO raw_infoclimat." + table +
            " (" + ", ".join(COLUMNS) + ", _sdc_extracted_at)"
            " VALUES (" + placeholders + ")"
            " ON CONFLICT (dh_utc) DO NOTHING;",
            values + [now_utc],
        )
        inserted += cur.rowcount
    conn.commit()
    print(f"{table}: {len(records)} releves recuperes, {inserted} nouveaux inseres")
    total += inserted

cur.close()
conn.close()
print(f"Total: {total} nouveaux releves ({START} -> {END})")
