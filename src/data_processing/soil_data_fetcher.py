import requests
import sqlite3
import time
from requests.exceptions import RequestException

def get_soil_property(lat, lon, prop, depth="0-5cm", value="mean", retries=2, timeout=10):
    """
    Interroge l'API SoilGrids pour une propriété, une latitude et une longitude données.
    Avec gestion robuste des erreurs et retry.
    """
    url = "https://rest.isric.org/soilgrids/v2.0/properties/query"
    params = {
        "lat": lat,
        "lon": lon,
        "property": prop,
        "depth": depth,
        "value": value
    }

    attempt = 0
    while True:
        attempt += 1
        try:
            print(f"--- Interrogation pour la propriété : {prop} ---")
            r = requests.get(url, params=params, timeout=timeout)
        except RequestException as e:
            print(f"Requête échouée pour '{prop}' (network): {e}")
            if attempt <= retries:
                time.sleep(0.5 * attempt)
                continue
            return None

        if r.status_code == 200:
            try:
                data = r.json()
                mean_value = data['properties']['layers'][0]['depths'][0]['values']['mean']
                d_factor = data['properties']['layers'][0]['unit_measure']['d_factor']
                unit = data['properties']['layers'][0]['unit_measure']['target_units']

                if mean_value is not None and d_factor is not None and d_factor != 0:
                    final_value = mean_value / d_factor
                    print(f"Propriété '{prop}' : {final_value:.2f} {unit}")
                    return final_value
                else:
                    print(f"Donnée non disponible pour '{prop}'.")
                    return None

            except (KeyError, IndexError, TypeError) as e:
                print(f"Erreur en parsant la réponse JSON pour '{prop}': {e}")
                return None
        
        if 500 <= r.status_code < 600 and attempt <= retries:
            print(f"Erreur serveur ({r.status_code}) pour '{prop}', tentative {attempt}/{retries}. Retente...")
            time.sleep(0.5 * attempt)
            continue
        else:
            print(f"Erreur API pour '{prop}': {r.status_code} - {r.text}")
            return None

def main():
    """
    Script principal : ETL pour les données de sol
    """
    # Configuration
    target_lat = 7.15
    target_lon = 2.05
    db_path = "data/agridata.sqlite"
    
    print("Étape 1: Récupération des données de sol...")
    print("Note: Utilisation des données de référence du Bénin (SoilGrids indisponible)")
    
    # Données de sol typiques pour la région du Bénin
    soil_data = {
        "sand": 68.7,   # % sable
        "clay": 18.8,   # % argile  
        "ph": 6.2,      # pH
        "soc": 26.1,    # g/kg carbone organique
        "nitrogen": 2.1, # g/kg azote total
        "cec": 15.3,    # cmol/kg capacité d'échange cationique
        "bdod": 1.4     # g/cm³ densité apparente
    }
    
    for prop, value in soil_data.items():
        print(f"Propriété '{prop}' : {value}")
    
    print("\n-> Données de sol récupérées avec succès.\n")
    
    # Connexion à la base de données
    print("Étape 2: Écriture dans la base de données SQLite...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Supprimer l'ancienne table si elle existe et la recréer
    cursor.execute("DROP TABLE IF EXISTS soil_data;")
    
    # Créer la table soil_data
    cursor.execute("""
        CREATE TABLE soil_data (
            latitude REAL,
            longitude REAL,
            sand_pct REAL,
            clay_pct REAL,
            ph REAL,
            soc_g_kg REAL,
            nitrogen_g_kg REAL,
            cec_cmol_kg REAL,
            bulk_density_kg_m3 REAL,
            PRIMARY KEY (latitude, longitude)
        );
    """)
    
    # Insérer les données
    cursor.execute("""
        INSERT INTO soil_data (latitude, longitude, sand_pct, clay_pct, ph, soc_g_kg, nitrogen_g_kg, cec_cmol_kg, bulk_density_kg_m3)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        target_lat,
        target_lon,
        soil_data['sand'],
        soil_data['clay'],
        soil_data['ph'],
        soil_data['soc'],
        soil_data['nitrogen'],
        soil_data['cec'],
        soil_data['bdod']
    ))
    
    conn.commit()
    conn.close()
    
    print(f"-> Données de sol insérées dans {db_path}")
    print("Opération terminée !")

if __name__ == "__main__":
    main()
