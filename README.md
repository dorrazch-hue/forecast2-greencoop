# Forecast 2.0 — Pipeline de données météo

**GreenCoop | Hauts-de-France | Data Engineering**

Pipeline ELT intégrant 6 stations météo semi-professionnelles pour alimenter les modèles de prévision de la demande électrique du projet Forecast 2.0.

---

## Résultats

| Indicateur | Valeur |
|---|---|
| Stations intégrées | 6 (InfoClimat + Weather Underground) |
| Observations totales | 9 463 (dédupliquées, une ligne par station et par horodatage) |
| Tests de qualité | 14/14 PASS (validés en local et en production AWS) |
| Pipeline automatisé | InfoClimat via Meltano — période configurable via .env |
| Données historiques | InfoClimat (JSON) + Weather Underground (Excel) — semaine du 1-7 octobre 2024 |
| Données fraîches | InfoClimat jusqu'au 8 juillet 2026 (relevés toutes les 10 min) |
| Déploiement | AWS RDS PostgreSQL (eu-west-3 Paris) |

---

## Sources de données

### Réseau InfoClimat — Pipeline automatisé (Meltano)
| Station | Code | Données |
|---|---|---|
| Bergues | 000R5 | Automatique (relevés 10 min) + historique 1-7 oct. 2024 |
| Hazebrouck | STATIC0010 | Automatique (relevés 10 min) + historique 1-7 oct. 2024 |
| Armentières | 00052 | Historique 1-7 octobre 2024 |
| Lille-Lesquin | 07015 | Historique 5-7 octobre 2024 |

> La période de synchronisation est configurable via les variables INFOCLIMAT_START / INFOCLIMAT_END du fichier .env (pas de dates en dur dans le code). Un script de secours `load_infoclimat_api.py` (API identique, mêmes tables, même clé de déduplication) est fourni pour les postes où une politique de sécurité bloque les exécutables des plugins Meltano.

### Réseau Weather Underground — Fichiers Excel manuels
| Station | Code | Données |
|---|---|---|
| La Madeleine (FR) | ILAMAD25 | Historique 1-7 octobre 2024 (relevés ~5 min) |
| Ichtegem (BE) | IICHTE19 | Historique 1-7 octobre 2024 (relevés ~5 min) |

> Note : l'API Weather Underground n'est pas accessible publiquement sans posséder une station enregistrée. Les données ont été intégrées via des fichiers Excel fournis par l'équipe (un onglet par jour, nommage JJMMAA). Les fichiers sont à placer dans forecast_meltano/data/ (voir README du dossier).
>
> Les sources historiques InfoClimat et Weather Underground couvrent la même semaine (1-7 octobre 2024), ce qui permet aux Data Scientists de croiser les relevés des 6 stations sur une période commune.

---

## Stack technique

| Outil | Version | Rôle |
|---|---|---|
| Python | 3.11 | Scripts d'ingestion |
| Meltano | 4.2.0 | ELT automatisé InfoClimat |
| DBT | 1.8.0 | Transformation, tests, documentation |
| PostgreSQL | 15 local / 18 RDS | Stockage |
| AWS RDS | db.t4g.micro Free Tier | Production |

---

## Structure du projet

    forecast2-greencoop/
    ├── docker-compose.yml
    ├── migrate_to_rds.py
    ├── aws/
    │   ├── ecs-task-definition.json   (tâche Fargate cible)
    │   └── README.md                  (architecture de planification)
    ├── forecast_meltano/
    │   ├── meltano.yml            (dates configurables via .env)
    │   ├── schemas/
    │   │   ├── bergues.json
    │   │   └── hazebrouck.json
    │   ├── data/
    │   │   └── README.md          (instructions fichiers Excel WU)
    │   ├── load_infoclimat_api.py (script de secours API InfoClimat)
    │   ├── load_infoclimat_json.py
    │   └── load_weather_underground.py
    └── forecast_dbt/
        ├── dbt_project.yml
        ├── packages.yml
        └── models/
            ├── staging/       (8 modèles - vues)
            ├── intermediate/  (1 modèle - vue, union + déduplication)
            └── marts/         (2 modèles - tables + tests)

---

## Schéma en étoile (DBT Marts)

    dim_weather_stations          fct_weather_observations
    station_key (PK) <----------- station_key (FK)
    station_id                    observed_at_utc
    station_name                  temperature_celsius
    latitude / longitude          pressure_hpa
    elevation_m                   humidity_percent
    network                       wind_speed_kmh
    hardware / software           rain_1h_mm / uv_index

---

## Qualité des données : 14/14 tests PASS

**Structurels (8)**
- unique, not_null sur les clés de la dimension
- not_null sur observed_at_utc et station_key (faits)
- relationships : clé étrangère station_key entre faits et dimension
- unicité (station_key, observed_at_utc) : une seule ligne par station et par horodatage dans la table de faits (dbt_utils.unique_combination_of_columns)

**Métier (6) via dbt_utils**
- Température : -25°C à 45°C (Hauts-de-France)
- Humidité : 0 à 100 %
- Pression : 870 à 1 085 hPa
- Vent : 0 à 250 km/h
- UV : 0 à 16
- Réseau : infoclimat ou weather_underground

**Protections en amont (couche RAW)**
- Clés primaires (id_station, dh_utc) sur les tables chargées par script : les rechargements accidentels ne créent aucun doublon (ON CONFLICT DO NOTHING)
- Déduplication dans le modèle intermediate en cas de recouvrement entre le flux Meltano et les données historiques

---

## Lancer le projet

    # 1. Démarrer PostgreSQL local
    docker compose up -d

    # 2. Activer l'environnement Python
    venv\Scripts\activate

    # 3. Configurer les variables d'environnement
    # Créer forecast_meltano/.env avec :
    # TAP_INFOCLIMAT_TOKEN=votre_token
    # RDS_PASSWORD=votre_mdp_rds
    # INFOCLIMAT_START=2026-07-01
    # INFOCLIMAT_END=2026-07-08

    # 4. Pipeline InfoClimat (automatique)
    cd forecast_meltano
    meltano run tap-infoclimat target-postgres
    # (ou, si les plugins Meltano sont bloqués par la politique de sécurité du poste :)
    python load_infoclimat_api.py

    # 5. Ingestion données historiques JSON
    python load_infoclimat_json.py

    # 6. Ingestion Weather Underground
    # Placer les fichiers Excel dans forecast_meltano/data/
    python load_weather_underground.py

    # 7. Transformations DBT (local)
    cd ../forecast_dbt
    dbt run
    dbt test

    # 8. Migration des données brutes vers AWS puis transformations en production
    python ../migrate_to_rds.py
    dbt run --target prod
    dbt test --target prod

---

## Sécurité

- Secrets en variables d'environnement (.env non versionné)
- Alerte GitGuardian détectée et corrigée en juin 2026
- Profil DBT prod utilise env_var('RDS_PASSWORD')
- .gitignore : venv/, .meltano/, .env, fichiers de données volumineux

---

## Supervision en place et perspectives

**Déjà actif sur AWS :**
- Sauvegardes automatiques RDS (rétention 7 jours)
- Monitoring CloudWatch : métriques RDS (CPU, connexions, stockage) et
  alarme `forecast2-db-cpu-alarm` (seuil CPU > 80 %, moyenne 5 min)

**Perspectives d'évolution :**
- **Planification cloud (ECS)** : exécution automatique de Meltano et DBT
  via une tâche ECS Fargate déclenchée par EventBridge, logs applicatifs
  centralisés dans CloudWatch (driver awslogs). Définition de tâche et
  étapes de déploiement versionnées dans le dossier `aws/`.
- **AWS Secrets Manager** : migration des secrets du .env avec rotation
  automatique du mot de passe RDS.
- **Weather Underground** : ingestion via fichiers Excel par conception —
  l'API n'est pas accessible sans posséder une station enregistrée.

---

Cherif Dorra : Data Engineer — GreenCoop Hauts-de-France | Forecast 2.0 | Juillet 2026
