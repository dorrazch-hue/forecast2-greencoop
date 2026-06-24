# Forecast 2.0 — Pipeline de données météo

**GreenCoop | Hauts-de-France | Data Engineering**

Pipeline ELT automatisé intégrant 6 stations météo semi-professionnelles pour alimenter les modèles de prévision de la demande électrique du projet Forecast 2.0.

---

## Résultats

| Indicateur | Valeur |
|---|---|
| Stations intégrées | 6 (InfoClimat + Weather Underground) |
| Observations totales | 6 471 |
| Tests de qualité | 13/13 PASS |
| Déploiement | AWS RDS PostgreSQL (eu-west-3 Paris) |

---

## Sources de données

### Réseau InfoClimat
| Station | Code | Statut |
|---|---|---|
| Bergues | 000R5 | Actif — pipeline Meltano automatisé |
| Hazebrouck | STATIC0010 | Actif — pipeline Meltano automatisé |
| Armentières | 00052 | Données historiques (oct 2024) |
| Lille-Lesquin | 07015 | Données historiques (oct 2024) |

### Réseau Weather Underground
| Station | Code | Statut |
|---|---|---|
| La Madeleine (FR) | ILAMAD25 | Données historiques (jan-jul 2024) |
| Ichtegem (BE) | IICHTE19 | Données historiques (jan-jul 2024) |

---

## Stack technique

| Outil | Version | Rôle |
|---|---|---|
| Python | 3.11 | Scripts d'ingestion |
| Meltano | 4.2.0 | ELT automatisé (remplace Airbyte) |
| DBT | 1.8.0 | Transformation, tests, documentation |
| PostgreSQL | 15 local / 18 RDS | Stockage |
| AWS RDS | db.t4g.micro | Production |

---

## Structure du projet

    forecast2-greencoop/
    ├── docker-compose.yml
    ├── migrate_to_rds.py
    ├── forecast_meltano/
    │   ├── meltano.yml
    │   ├── schemas/
    │   ├── load_infoclimat_json.py
    │   └── load_weather_underground.py
    └── forecast_dbt/
        ├── dbt_project.yml
        ├── packages.yml
        └── models/
            ├── staging/      (6 modèles)
            ├── intermediate/ (1 modèle)
            └── marts/        (2 modèles + tests)

---

## Schéma en étoile

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

- **Structurels** : unique, not_null, relationships (clé étrangère)
- **Métier** : température (-25°C à 45°C), humidité (0-100%), pression (870-1085 hPa), vent (0-250 km/h), UV (0-16), réseau

---

## Sécurité

- Secrets en variables d'environnement (.env non versionné)
- Alerte GitGuardian détectée et corrigée immédiatement (juin 2026)
- Profil DBT prod utilise env_var RDS_PASSWORD

---

## Points en attente

- **Weather Underground API** : accès bloqué (nécessite une station personnelle enregistrée)
- **ECS + CloudWatch + Secrets Manager** : automatisation AWS à venir
- **Armentières / Lille-Lesquin** : données limitées à octobre 2024

---

**Auteur** : Data Engineer — GreenCoop Hauts-de-France | Forecast 2.0 | Juin 2026
