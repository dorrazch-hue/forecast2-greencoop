import psycopg2

RDS_HOST = "forecast2-db.chqu82ekqm8t.eu-west-3.rds.amazonaws.com"
RDS_USER = "forecast_user"
RDS_PASS = "Forecast2026!"
RDS_DB = "postgres"

local = psycopg2.connect(host="localhost", port=5432, database="forecast_db", user="forecast_user", password="forecast_pass")
rds = psycopg2.connect(host=RDS_HOST, port=5432, database=RDS_DB, user=RDS_USER, password=RDS_PASS)

local_cur = local.cursor()
rds_cur = rds.cursor()

tables = {
    "raw_infoclimat": ["bergues", "hazebrouck", "bergues_hist", "hazebrouck_hist", "armentieres", "lille_lesquin"],
    "raw_weather_underground": ["la_madeleine", "ichtegem"]
}

for schema, tbls in tables.items():
    rds_cur.execute(f"CREATE SCHEMA IF NOT EXISTS {schema};")
    for table in tbls:
        print(f"Migration {schema}.{table}...")
        local_cur.execute(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_schema='{schema}' AND table_name='{table}' ORDER BY ordinal_position;")
        columns = local_cur.fetchall()
        if not columns:
            print(f"  -> Table vide ou inexistante, ignoree")
            continue
        col_defs = ", ".join([f"{c[0]} {c[1]}" for c in columns])
        col_names = ", ".join([c[0] for c in columns])
        rds_cur.execute(f"DROP TABLE IF EXISTS {schema}.{table};")
        rds_cur.execute(f"CREATE TABLE {schema}.{table} ({col_defs});")
        local_cur.execute(f"SELECT {col_names} FROM {schema}.{table};")
        rows = local_cur.fetchall()
        if rows:
            placeholders = ", ".join(["%s"] * len(columns))
            rds_cur.executemany(f"INSERT INTO {schema}.{table} ({col_names}) VALUES ({placeholders})", rows)
        rds.commit()
        print(f"  -> {len(rows)} lignes migrees")

print("\nMigration terminee !")
local_cur.close()
rds_cur.close()
local.close()
rds.close()