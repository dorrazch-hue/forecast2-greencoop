# API Seattle Energy Prediction

## Description
API de prédiction de la consommation énergétique des bâtiments non-résidentiels 
de Seattle, développée avec BentoML et déployée sur Google Cloud Run.

## URL de l'API déployée
https://seattle-energy-api-jfbg37q7kq-ew.a.run.app

## Interface Swagger
https://seattle-energy-api-jfbg37q7kq-ew.a.run.app

## Lancer l'API en local
```bash
bentoml serve service:SeattleEnergyService
```

## Tester l'API en local
```bash
curl -X POST http://localhost:3000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "batiment": {
      "PropertyGFATotal": 50000,
      "NumberofBuildings": 1,
      "NumberofFloors": 5,
      "YearBuilt": 1990,
      "PrimaryPropertyType": "Small- and Mid-Sized Office",
      "HasGas": 1,
      "HasSteam": 0,
      "Latitude": 47.6,
      "UsageMultiple": 0
    }
  }'
```

## Tester l'API sur le Cloud
```bash
curl -X POST https://seattle-energy-api-jfbg37q7kq-ew.a.run.app/predict \
  -H "Content-Type: application/json" \
  -d '{
    "batiment": {
      "PropertyGFATotal": 50000,
      "NumberofBuildings": 1,
      "NumberofFloors": 5,
      "YearBuilt": 1990,
      "PrimaryPropertyType": "Small- and Mid-Sized Office",
      "HasGas": 1,
      "HasSteam": 0,
      "Latitude": 47.6,
      "UsageMultiple": 0
    }
  }'
```

## Redéployer sur GCP Cloud Run
```bash
gcloud run deploy seattle-energy-api \
  --image gcr.io/project-2e4c7d68-38e1-426b-af0/seattle_energy_service:v3 \
  --platform managed \
  --region europe-west1 \
  --allow-unauthenticated \
  --port 3000
```

## Arrêter le service Cloud Run
```bash
gcloud run services delete seattle-energy-api --region europe-west1
```

## Fichiers du projet
- `save_model.py` : sauvegarde et entraînement du modèle avec BentoML
- `service.py` : logique de l'API et validation des données avec Pydantic
- `bentofile.yaml` : configuration du déploiement Docker

## Format des données acceptées
| Champ | Type | Description | Contraintes |
|---|---|---|---|
| PropertyGFATotal | float | Surface totale en pieds carrés | > 0 |
| NumberofBuildings | int | Nombre de bâtiments | >= 1 |
| NumberofFloors | int | Nombre d'étages | >= 1 |
| YearBuilt | int | Année de construction | 1800-2016 |
| PrimaryPropertyType | str | Type de bâtiment | Voir liste |
| HasGas | int | Présence de gaz | 0 ou 1 |
| HasSteam | int | Présence de vapeur | 0 ou 1 |
| Latitude | float | Latitude Seattle | 47.0-48.0 |
| UsageMultiple | int | Usage multiple | 0 ou 1 |

## Types de bâtiments acceptés
- Small- and Mid-Sized Office
- Warehouse
- Large Office
- K-12 School
- Retail Store
- Hotel
- Other
- Mixed Use Property
- Worship Facility
- Distribution Center
- Hospital
- Residence Hall
- Medical Office
- Laboratory
- Refrigerated Warehouse
- Restaurant
- Low-Rise Multifamily
- Office
- Senior Care Community
- University
- Self-Storage Facility
- Supermarket / Grocery Store