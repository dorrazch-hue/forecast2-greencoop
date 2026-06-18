\# Forecast 2.0 - Pipeline de données météo (GreenCoop)



Pipeline ELT pour le projet Forecast 2.0 : ingestion des données météo de stations InfoClimat et Weather Underground, transformation via DBT, en vue d'améliorer les modèles de prévision de la demande électrique.



\## Stack technique

\- \*\*PostgreSQL\*\* (Docker, cible RDS sur AWS à terme)

\- \*\*Meltano\*\* (ELT, remplace Airbyte pour des raisons de stabilité)

\- \*\*DBT\*\* (transformation, staging/intermediate/marts, schéma en étoile)



\## Structure

\- `docker-compose.yml` : déploiement local de PostgreSQL

\- `forecast\_meltano/` : configuration Meltano (extracteurs, chargeurs)

\- `forecast\_dbt/` : projet DBT (modèles, tests, documentation)



\## Statut

Voir le journal de bord du projet pour le détail de l'avancement par étape.

