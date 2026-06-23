import psycopg2

# Connexion locale
local = psycopg2.connect(
    host="localhost", port=5432,
    database="forecast_db", user="forecast_user", password="forecast_pass"
)

# Connexion RDS
rds = psycopg2.connect(
    host="forecast2-db.chqu82ekqm8t.eu-west-3.rds.amazonaws.com",
    port=5432, database="postgres",
    user="forecast_user", password="Forecast2026!"
)

local_cur = local.cursor()
rds_cur = rds.cursor()

# Créer les schémas sur RDS
rds_cur.execute("CREATE SCHEMA IF NOT EXISTS raw_infoclimat;")
rds_cur.execute("CREATE SCHEMA IF NOT EXISTS raw_weather_underground;")
rds_cur.execute("CREATE SCHEMA IF NOT EXISTS public;")
rds.commit()

print("Schemas crees sur RDS !")
print("Migration prete - a completer lors de la prochaine session")

local_cur.close()
rds_cur.close()
local.close()
rds.close()