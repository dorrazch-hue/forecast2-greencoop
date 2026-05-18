import bentoml
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import cross_validate
from sklearn.preprocessing import StandardScaler

# ============================================
# 1. CHARGEMENT DES DONNÉES
# ============================================
building_consumption = pd.read_csv("/Users/dorra/Desktop/2016_Building_Energy_Benchmarking.csv")

# ============================================
# 2. NETTOYAGE (même logique que le notebook)
# ============================================
# Filtrage non-résidentiels
residential_types = ['Multifamily LR (1-4)', 'Multifamily MR (5-9)', 'Multifamily HR (10+)']
building_consumption = building_consumption[
    ~building_consumption['BuildingType'].isin(residential_types)
]

# Suppression consommations nulles/négatives
building_consumption = building_consumption[
    building_consumption['SiteEnergyUse(kBtu)'] > 0
]

# Suppression surfaces nulles
building_consumption = building_consumption[
    building_consumption['PropertyGFATotal'] > 0
]

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
    'SiteEnergyUse(kBtu)'
]

df_model = building_consumption[colonnes_a_garder].copy()
df_model['Target'] = np.log1p(df_model['SiteEnergyUse(kBtu)'])

# Suppression outliers
q_low = df_model['Target'].quantile(0.01)
q_high = df_model['Target'].quantile(0.99)
df_model = df_model[
    (df_model['Target'] >= q_low) & 
    (df_model['Target'] <= q_high)
]

# Separation X et y
y = df_model['Target']
X = df_model.drop(columns=['Target', 'SiteEnergyUse(kBtu)'])
X = pd.get_dummies(X, columns=['PrimaryPropertyType', 'TrancheAge', 'ZoneGeo'])

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
print(f"Modele entraine sur {len(X)} batiments avec {X.shape[1]} features")

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