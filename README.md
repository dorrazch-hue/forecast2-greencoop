\# Forecast 2.0 — Pipeline de données météo



\*\*GreenCoop | Hauts-de-France | Data Engineering\*\*



Pipeline ELT automatisé intégrant 6 stations météo semi-professionnelles pour alimenter les modèles de prévision de la demande électrique du projet Forecast 2.0.



\---



\## Résultats



| Indicateur | Valeur |

|---|---|

| Stations intégrées | 6 (InfoClimat + Weather Underground) |

| Observations totales | 6 471 |

| Tests de qualité | 13/13 PASS |

| Déploiement | AWS RDS PostgreSQL (eu-west-3 Paris) |



\---



\## Sources de données



\### Réseau InfoClimat

| Station | Code | Statut |

|---|---|---|

| Bergues | 000R5 | Actif — pipeline Meltano automatisé |

| Hazebrouck | STATIC0010 | Actif — pipeline Meltano automatisé |

| Armentières | 00052 | Données historiques (oct 2024) |

| Lille-Lesquin | 07015 | Données historiques (oct 2024) |



\### Réseau Weather Underground

| Station | Code | Statut |

|---|---|---|

| La Madeleine (FR) | ILAMAD25 | Données historiques (jan-jul 2024) |

| Ichtegem (BE) | IICHTE19 | Données historiques (jan-jul 2024) |



\---



\## Stack technique



| Outil | Version | Rôle |

|---|---|---|

| Python | 3.11 | Scripts d'ingestion, environnement |

| Meltano | 4.2.0 | ELT automatisé (remplace Airbyte) |

| DBT | 1.8.0 | Transformation, tests, documentation |

| PostgreSQL | 15 local / 18 RDS | Stockage |

| AWS RDS | db.t4g.micro | Production |



\---



\## Structure du projet

