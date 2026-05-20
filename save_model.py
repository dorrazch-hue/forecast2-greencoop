import bentoml
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import os

# ============================================
# 1. CHARGEMENT DES DONNÉES
# ============================================
csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "2016_Building_Energy_Benchmarking.csv")
building_consumption = pd.read_csv(csv_path)

# ============================================
# 2. NETTOYAGE
# ============================================
# Filtrage non-résidentiels
residential_types = ['Multifamily LR (1-4)', 'Multifamily MR (5-9)', 'Multifamily HR (10+)']
building_consumption = building_consumption[
    ~building_consumption['BuildingType'].isin(residential_types)
]

# Filtrage ComplianceStatus
building_consumption = building_consumption[
    building_consumption['ComplianceStatus'] == 'Compliant'
]

# Suppression des outliers marqués
building_consumption = building_consumption[
    ~building_consumption['Outlier'].isin(['Low outlier', 'High outlier'])
]

# Suppression consommations nulles/négatives
building_consumption = building_consumption[
    building_consumption['SiteEnergyUseWN(kBtu)'] > 0
]

# Suppression surfaces nulles
building_consumption = building_consumption[
    building_consumption['PropertyGFATotal'] > 0
]

print(f"Nombre de batiments apres nettoyage : {len(building_consumption)}")

# ============================================
# 3. FEATURE ENGINEERING
# ============================================
building_consumption['BuildingAge'] = 2016 - building_consumption['YearBuilt']

def tranche_age(age):
    if age <= 20:
        return 'Recent'
    elif age <= 50:
        return 'Moderne'
    elif age <= 80:
        return 'Ancien'
    else:
        return 'Tres ancien'

building_consumption['TrancheAge'] = building_consumption['BuildingAge'].apply(tranche_age)

building_consumption['UsageMultiple'] = (
    building_consumption['NumberofBuildings'] > 1
).astype(int)

building_consumption['HasGas'] = (
    building_consumption['NaturalGas(kBtu)'] > 0
).astype(int)

building_consumption['HasSteam'] = (
    building_consumption['SteamUse(kBtu)'] > 0
).astype(int)

def zone_geo(lat):
    if lat >= 47.65:
        return 'Nord'
    elif lat >= 47.58:
        return 'Centre'
    else:
        return 'Sud'

building_consumption['ZoneGeo'] = building_consumption['Latitude'].apply(zone_geo)

# ============================================
# 4. PREPARATION DES FEATURES
# ============================================
colonnes_a_garder = [
    'PropertyGFATotal', 'NumberofBuildings', 'NumberofFloors',
    'PrimaryPropertyType', 'BuildingAge', 'UsageMultiple',
    'HasGas', 'HasSteam', 'TrancheAge', 'ZoneGeo',
    'SiteEnergyUseWN(kBtu)'
]

df_model = building_consumption[colonnes_a_garder].copy()
df_model['Target'] = np.log1p(df_model['SiteEnergyUseWN(kBtu)'])

# Suppression outliers quantiles
q_low = df_model['Target'].quantile(0.01)
q_high = df_model['Target'].quantile(0.99)
df_model = df_model[
    (df_model['Target'] >= q_low) &
    (df_model['Target'] <= q_high)
]

# Separation X et y
y = df_model['Target']
X = df_model.drop(columns=['Target', 'SiteEnergyUseWN(kBtu)'])
X = pd.get_dummies(X, columns=['PrimaryPropertyType', 'TrancheAge', 'ZoneGeo'])

print(f"Nombre de batiments pour la modelisation : {len(X)}")
print(f"Nombre de features : {X.shape[1]}")

# ============================================
# 5. ENTRAINEMENT DU MODELE
# ============================================
model = RandomForestRegressor(
    max_depth=15,
    min_samples_split=10,
    n_estimators=100,
    random_state=42
)
model.fit(X, y)
print("Modele entraine avec succes !")

# ============================================
# 6. SAUVEGARDE AVEC BENTOML
# ============================================
saved_model = bentoml.sklearn.save_model(
    "seattle_energy_model",
    model,
    custom_objects={
        "feature_names": list(X.columns)
    }
)

print(f"Modele sauvegarde : {saved_model}")
print("Sauvegarde terminee !")