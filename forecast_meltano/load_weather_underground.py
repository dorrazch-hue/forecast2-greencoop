import pandas as pd
import psycopg2
from openpyxl import load_workbook
from datetime import datetime

# Connexion PostgreSQL
conn = psycopg2.connect(
    host="localhost", port=5432,
    database="forecast_db", user="forecast_user", password="forecast_pass"
)
cur = conn.cursor()

# Création du schéma et des tables
cur.execute("CREATE SCHEMA IF NOT EXISTS raw_weather_underground;")

for table in ['la_madeleine', 'ichtegem']:
    cur.execute(f"""
        CREATE TABLE IF NOT EXISTS raw_weather_underground.{table} (
            observed_at TIMESTAMP,
            temperature_f VARCHAR,
            dew_point_f VARCHAR,
            humidity_pct VARCHAR,
            wind_direction VARCHAR,
            wind_speed_mph VARCHAR,
            wind_gust_mph VARCHAR,
            pressure_in VARCHAR,
            precip_rate_in VARCHAR,
            precip_accum_in VARCHAR,
            uv_index VARCHAR,
            solar_wm2 VARCHAR
        );
    """)
conn.commit()

def fahrenheit_to_celsius(f_str):
    if f_str and 'F' in str(f_str):
        try:
            return str(round((float(str(f_str).replace('°F','').strip()) - 32) * 5/9, 2))
        except:
            return None
    return None

def mph_to_kmh(mph_str):
    if mph_str and 'mph' in str(mph_str):
        try:
            return str(round(float(str(mph_str).replace('mph','').strip()) * 1.60934, 2))
        except:
            return None
    return None

def inches_to_mm(in_str):
    if in_str and 'in' in str(in_str):
        try:
            return str(round(float(str(in_str).replace('in','').strip()) * 25.4, 2))
        except:
            return None
    return None

def excel_time_to_timestamp(sheet_name, time_val):
    month = int(sheet_name[:2])
    year = int('20' + sheet_name[4:6])
    try:
        minutes = round(float(time_val) * 24 * 60)
        hours = minutes // 60
        mins = minutes % 60
        return datetime(year, month, 1, hours % 24, mins)
    except:
        return None

files = {
    'la_madeleine': r'C:\Users\zitou\Downloads\Weather+Underground+-+La+Madeleine,+FR.xlsx',
    'ichtegem': r'C:\Users\zitou\Downloads\Weather+Underground+-+Ichtegem,+BE.xlsx',
}

total = 0
for table, filepath in files.items():
    wb = load_workbook(filepath, read_only=True)
    count = 0
    for sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
        rows = list(ws.iter_rows(values_only=True))
        for row in rows[1:]:
            if not row or row[0] is None:
                continue
            ts = excel_time_to_timestamp(sheet_name, row[0])
            cur.execute(f"""
                INSERT INTO raw_weather_underground.{table}
                (observed_at, temperature_f, dew_point_f, humidity_pct,
                 wind_direction, wind_speed_mph, wind_gust_mph, pressure_in,
                 precip_rate_in, precip_accum_in, uv_index, solar_wm2)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT DO NOTHING;
            """, (
                ts,
                fahrenheit_to_celsius(row[1]),
                fahrenheit_to_celsius(row[2]),
                str(row[3]).replace('%','').strip() if row[3] else None,
                str(row[4]) if row[4] else None,
                mph_to_kmh(row[5]),
                mph_to_kmh(row[6]),
                inches_to_mm(row[7]),
                inches_to_mm(row[8]),
                inches_to_mm(row[9]),
                str(row[10]) if row[10] else None,
                str(row[11]).replace('w/m²','').strip() if row[11] else None,
            ))
            count += 1
    conn.commit()
    print(f"{table}: {count} relevés chargés")
    total += count

print(f"\nTotal: {total} relevés chargés avec succès !")
cur.close()
conn.close()