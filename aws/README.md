# Architecture cible — Exécution planifiée sur AWS ECS

Ce dossier contient la définition de la tâche ECS Fargate qui exécutera
automatiquement le pipeline complet (Meltano + DBT) en production.
**Statut : architecture définie, déploiement prévu en prochaine itération.**

## Fonctionnement cible

    EventBridge Scheduler (cron : toutes les heures)
            │ déclenche
            ▼
    Tâche ECS Fargate  ──  ecs-task-definition.json
      1. meltano run tap-infoclimat target-postgres   (ingestion)
      2. dbt run --target prod                        (transformation)
      3. dbt test --target prod                       (qualité)
            │ écrit                          │ logs (driver awslogs)
            ▼                                ▼
      AWS RDS PostgreSQL              CloudWatch Logs (/ecs/forecast2-elt)

## Choix de conception

- **Fargate** : pas de serveur à gérer, facturation à la seconde d'exécution —
  adapté à une tâche courte exécutée périodiquement.
- **Secrets Manager** : le token InfoClimat et le mot de passe RDS sont
  référencés en tant que secrets (bloc `secrets`), jamais en clair dans la
  définition — conformément au point de vigilance de la mission.
- **awslogs** : les logs de Meltano et DBT sont centralisés dans CloudWatch,
  dans le groupe `/ecs/forecast2-elt`, complétant le monitoring déjà actif
  (métriques RDS + alarme `forecast2-db-cpu-alarm`).
- **Dates dynamiques** : les variables INFOCLIMAT_START/END seront calculées
  au lancement (fenêtre glissante de 7 jours) par le point d'entrée du
  conteneur.

## Étapes de déploiement 

1. Construire l'image Docker (Python 3.11 + Meltano + DBT + le projet) et
   la pousser sur Amazon ECR : `forecast2-elt:latest`
2. Créer les secrets dans AWS Secrets Manager
   (`forecast2/infoclimat-token`, `forecast2/rds-password`)
3. Créer le groupe de logs CloudWatch `/ecs/forecast2-elt`
4. Enregistrer la définition de tâche :
   `aws ecs register-task-definition --cli-input-json file://ecs-task-definition.json`
5. Autoriser le Security Group de la tâche à joindre RDS (port 5432)
6. Créer la planification EventBridge Scheduler vers la tâche
