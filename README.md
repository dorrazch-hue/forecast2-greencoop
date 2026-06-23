\# Forecast 2.0 - Pipeline de donnees meteo (GreenCoop)



Pipeline ELT pour le projet Forecast 2.0 : ingestion des donnees meteo de stations InfoClimat et Weather Underground, transformation via DBT, en vue d'ameliorer les modeles de prevision de la demande electrique.



\## Stack technique



\- PostgreSQL (Docker, cible RDS sur AWS a terme)

\- Meltano (ELT, remplace Airbyte pour des raisons de stabilite)

\- DBT (transformation, staging/intermediate/marts, schema en etoile)



\## Structure



\- docker-compose.yml : deploiement local de PostgreSQL

\- forecast\_meltano/ : configuration Meltano (extracteurs, chargeurs)

\- forecast\_dbt/ : projet DBT (modeles, tests, documentation)



\## Statut



Voir le journal de bord du projet pour le detail de l'avancement par etape.

