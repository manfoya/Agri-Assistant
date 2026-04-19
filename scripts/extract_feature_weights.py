"""Extraction des poids des variables (Feature Importance).

Ce script entraine un Random Forest sur le dataset de recommandation
de cultures de Kaggle (Inde) pour comprendre le poids relatif
de chaque variable (N, P, K, temperature, humidite, pH, pluie).
Ces poids nous aideront a calibrer notre algorithme de matching.
"""

import os
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

# Chemin vers le dataset Kaggle telecharge
DATASET_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data",
    "training",
    "Crop_recommendation.csv"
)

def extract_weights():
    """Charge les donnees, entraine le modele et affiche l'importance des variables."""
    if not os.path.exists(DATASET_PATH):
        print(f"Erreur : Le fichier {DATASET_PATH} est introuvable.")
        return

    print("--- Chargement des donnees Kaggle ---")
    df = pd.read_csv(DATASET_PATH)
    print(f"Dimensions du dataset : {df.shape[0]} lignes, {df.shape[1]} colonnes.")
    
    # Separer les features (X) de la cible (y)
    X = df.drop(columns=["label"])
    y = df["label"]
    
    print("\n--- Entrainement du Random Forest ---")
    # On utilise un Random Forest classique avec 100 arbres
    rf_model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    rf_model.fit(X, y)
    
    # Extraction de l'importance des features
    importances = rf_model.feature_importances_
    features = X.columns
    
    # Creation d'un dataframe pour un affichage propre
    weights_df = pd.DataFrame({
        "Variable": features,
        "Poids_Pourcentage": importances * 100
    })
    
    # Trier par importance decroissante
    weights_df = weights_df.sort_values(by="Poids_Pourcentage", ascending=False).reset_index(drop=True)
    
    print("\n--- Resultats de l'analyse (Poids des variables) ---")
    print(weights_df.to_string(index=False, float_format=lambda x: f"{x:.2f}%"))
    
    print("\nAnalyse :")
    print("1. Ce modele nous montre ce qui discrimine le plus les cultures dans ce dataset.")
    print("2. L'eau (Pluie + Humidite) et l'Azote (N) ou Potassium (K) semblent etre des facteurs majeurs.")
    print("3. Pour Agri-Assistant, nous utiliserons ces proportions pour ponderer notre algorithme.")

if __name__ == "__main__":
    extract_weights()
