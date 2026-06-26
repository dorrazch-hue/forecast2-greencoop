# Forecast 2.0 — Pipeline de données météo

**GreenCoop | Hauts-de-France | Data Engineering**

Pipeline ELT intégrant 6 stations météo semi-professionnelles pour alimenter les modèles de prévision de la demande électrique du projet Forecast 2.0.

---

## Résultats

| Indicateur | Valeur |
|---|---|
| Stations intégrées | 6 (InfoClimat + Weather Underground) |
| Observations totales | 6 471 |
| Tests de qualité | 13/13 PASS |
| Pipeline automatisé | InfoClimat via Meltano (données fraîches) |
| Données historiques | Weather Underground via fichiers Excel (jan-jul 2024) |
| Déploiement | AWS RDS PostgreSQL (eu-west-3 Paris) |

---

## Sources de données

### Réseau InfoClimat — Pipeline automatisé (Meltano)
| Station | Code | Données |
|---|---|---|
| Bergues | 000R5 | Automatique — synchronisation toutes les 10 min |
| Hazebrouck | STATIC0010 | Automatique — synchronisation toutes les 10 min |
| Armentières | 00052 | Historique octobre 2024 |
| Lille-Lesquin | 07015 | Historique octobre 2024 |

### Réseau Weather Underground — Fichiers Excel manuels
| Station | Code | Données |
|---|---|---|
| La Madeleine (FR) | ILAMAD25 | Historique janvier-juillet 2024 |
| Ichtegem (BE) | IICHTE19 | Historique janvier-juillet 2024 |

> Note : l'API Weather Underground n'est pas accessible publiquement sans posséder une station personnelle enregistrée. Les données ont été intégrées via des fichiers Excel fournis par l'équipe. Les fichiers sont à placer dans forecast_meltano/data/ (voir README du dossier).

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
    ├── forecast_meltano/
    │   ├── meltano.yml
    │   ├── schemas/
    │   │   ├── bergues.json
    │   │   └── hazebrouck.json
    │   ├── data/
    │   │   └── README.md  (instructions fichiers Excel WU)
    │   ├── load_infoclimat_json.py
    │   └── load_weather_underground.py
    └── forecast_dbt/
        ├── dbt_project.yml
        ├── packages.yml
        └── models/
            ├── staging/       (6 modèles - vues)
            ├── intermediate/  (1 modèle - vue)
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
    hardware                      rain_1h_mm / uv_index

---

## Tests de qualité : 13/13 PASS

**Structurels (7)**
- unique, not_null sur les clés de la dimension
- not_null sur observed_at_utc et station_key (faits)
- relationships : clé étrangère station_key entre faits et dimension

**Métier (6) via dbt_utils**
- Température : -25°C à 45°C (Hauts-de-France)
- Humidité : 0 à 100 %
- Pression : 870 à 1 085 hPa
- Vent : 0 à 250 km/h
- UV : 0 à 16
- Réseau : infoclimat ou weather_underground

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

    # 4. Pipeline InfoClimat (automatique)
    cd forecast_meltano
    meltano run tap-infoclimat target-postgres

    # 5. Ingestion données historiques JSON
    python load_infoclimat_json.py

    # 6. Ingestion Weather Underground
    # Placer les fichiers Excel dans forecast_meltano/data/
    python load_weather_underground.py

    # 7. Transformations DBT (local)
    cd ../forecast_dbt
    dbt run
    dbt test

    # 8. Transformations DBT (production AWS)
    dbt run --target prod
    dbt test --target prod

---

## Sécurité

- Secrets en variables d'environnement (.env non versionné)
- Alerte GitGuardian détectée et corrigée en juin 2026
- Profil DBT prod utilise env_var('RDS_PASSWORD')
- .gitignore : venv/, .meltano/, .env, fichiers volumineux

---

## Points en attente

- **Weather Underground automatisation** : synchronisation manuelle via fichiers Excel — API non accessible sans posséder une station enregistrée
- **ECS + CloudWatch** : automatisation des tâches Meltano sur AWS
- **Secrets Manager** : rotation automatique des clés RDS
- **Armentières / Lille-Lesquin** : données limitées à octobre 2024 (stations peu actives sur l'API InfoClimat)

---

**Auteur** : Data Engineer — GreenCoop Hauts-de-France | Forecast 2.0 | Juin 2026
