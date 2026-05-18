import bentoml
import numpy as np
import pandas as pd
from pydantic import BaseModel, Field, validator

# ============================================
# VALIDATION DES DONNEES AVEC PYDANTIC
# ============================================

class BatimentInput(BaseModel):
    PropertyGFATotal: float = Field(..., gt=0, description="Surface totale en pieds carres")
    NumberofBuildings: int = Field(..., ge=1, description="Nombre de batiments (minimum 1)")
    NumberofFloors: int = Field(..., ge=1, description="Nombre d etages (minimum 1)")
    YearBuilt: int = Field(..., ge=1800, le=2016, description="Annee de construction")
    PrimaryPropertyType: str = Field(..., description="Type principal du batiment")
    HasGas: int = Field(..., ge=0, le=1, description="Presence de gaz (0 ou 1)")
    HasSteam: int = Field(..., ge=0, le=1, description="Presence de vapeur (0 ou 1)")
    Latitude: float = Field(..., ge=47.0, le=48.0, description="Latitude Seattle")
    UsageMultiple: int = Field(..., ge=0, le=1, description="Usage multiple (0 ou 1)")

    @validator('PrimaryPropertyType')
    def validate_property_type(cls, v):
        types_valides = [
            'Small- and Mid-Sized Office', 'Warehouse', 'Large Office',
            'K-12 School', 'Retail Store', 'Hotel', 'Other',
            'Mixed Use Property', 'Worship Facility', 'Distribution Center',
            'Hospital', 'Residence Hall', 'Medical Office', 'Laboratory',
            'Refrigerated Warehouse', 'Restaurant', 'Low-Rise Multifamily',
            'Office', 'Senior Care Community', 'University',
            'Self-Storage Facility', 'Supermarket / Grocery Store'
        ]
        if v not in types_valides:
            raise ValueError(f"Type invalide. Choisissez parmi : {types_valides}")
        return v


# ============================================
# CHARGEMENT DU MODELE
# ============================================
model_ref = bentoml.sklearn.get("seattle_energy_model:latest")
feature_names = model_ref.custom_objects["feature_names"]
sklearn_model = model_ref.load_model()


# ============================================
# DEFINITION DU SERVICE — syntaxe BentoML 1.x
# ============================================
@bentoml.service()
class SeattleEnergyService:

    def __init__(self):
        self.model = sklearn_model
        self.feature_names = feature_names

    @bentoml.api()
    def predict(self, batiment: BatimentInput) -> dict:

        # 1. Feature Engineering
        building_age = 2016 - batiment.YearBuilt

        def tranche_age(age):
            if age <= 20:
                return 'Recent'
            elif age <= 50:
                return 'Moderne'
            elif age <= 80:
                return 'Ancien'
            else:
                return 'Tres ancien'

        def zone_geo(lat):
            if lat >= 47.65:
                return 'Nord'
            elif lat >= 47.58:
                return 'Centre'
            else:
                return 'Sud'

        tranche = tranche_age(building_age)
        zone = zone_geo(batiment.Latitude)

        # 2. Construction du dataframe
        data = {
            'PropertyGFATotal': batiment.PropertyGFATotal,
            'NumberofBuildings': batiment.NumberofBuildings,
            'NumberofFloors': batiment.NumberofFloors,
            'BuildingAge': building_age,
            'UsageMultiple': batiment.UsageMultiple,
            'HasGas': batiment.HasGas,
            'HasSteam': batiment.HasSteam,
        }

        df = pd.DataFrame([data])

        # 3. One Hot Encoding
        df[f'PrimaryPropertyType_{batiment.PrimaryPropertyType}'] = 1
        df[f'TrancheAge_{tranche}'] = 1
        df[f'ZoneGeo_{zone}'] = 1

        # 4. Alignement des features
        for col in self.feature_names:
            if col not in df.columns:
                df[col] = 0
        df = df[self.feature_names]

        # 5. Prediction
        log_prediction = self.model.predict(df.values)
        prediction = np.expm1(log_prediction[0])

        return {
            "consommation_predite_kBtu": round(float(prediction), 2),
            "batiment_age": building_age,
            "zone_geographique": zone,
            "tranche_age": tranche,
            "message": f"Ce batiment devrait consommer environ {round(float(prediction)/1000000, 2)} millions de kBtu par an."
        }