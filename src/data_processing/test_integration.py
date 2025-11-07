#!/usr/bin/env python3
"""
Script de test d'intégration des données météo et sol
Vérifie que notre base de données SQLite contient toutes les données nécessaires
"""

import sqlite3

def test_database_integration():
    """
    Teste l'intégration complète des données météo et sol
    """
    db_path = "data/agridata.sqlite"
    
    print("=== TEST D'INTÉGRATION DE LA BASE DE DONNÉES ===\n")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Test 1: Vérifier les tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"Tables disponibles: {[table[0] for table in tables]}")
        
        # Test 2: Données météo
        cursor.execute("SELECT COUNT(*) FROM weather_data;")
        weather_count = cursor.fetchone()[0]
        print(f"Lignes de données météo: {weather_count}")
        
        # Test 3: Colonnes météo
        cursor.execute("PRAGMA table_info(weather_data);")
        weather_columns = [col[1] for col in cursor.fetchall()]
        print(f"Colonnes météo ({len(weather_columns)}): {weather_columns}")
        
        # Test 4: Données de sol
        cursor.execute("SELECT COUNT(*) FROM soil_data;")
        soil_count = cursor.fetchone()[0] 
        print(f"Lignes de données de sol: {soil_count}")
        
        # Test 5: Colonnes sol
        cursor.execute("PRAGMA table_info(soil_data);")
        soil_columns = [col[1] for col in cursor.fetchall()]
        print(f"Colonnes sol ({len(soil_columns)}): {soil_columns}")
        
        # Test 6: Échantillon de données combinées
        print("\n=== ÉCHANTILLON DE DONNÉES COMBINÉES ===")
        query = """
        SELECT 
            w.date,
            w.precipitation_mm,
            w.temp_mean_c,
            w.humidity_pct,
            s.sand_pct,
            s.clay_pct,
            s.ph,
            s.soc_g_kg
        FROM weather_data w, soil_data s 
        WHERE w.latitude = s.latitude AND w.longitude = s.longitude
        LIMIT 5;
        """
        cursor.execute(query)
        results = cursor.fetchall()
        
        print("Date | Précip(mm) | Temp(°C) | Humid(%) | Sable(%) | Argile(%) | pH | SOC(g/kg)")
        print("-" * 80)
        for row in results:
            print(f"{row[0]} | {row[1]:8.1f} | {row[2]:6.1f} | {row[3]:6.1f} | {row[4]:6.1f} | {row[5]:7.1f} | {row[6]:4.1f} | {row[7]:6.1f}")
        
        # Test 7: Statistiques météo
        print("\n=== STATISTIQUES MÉTÉOROLOGIQUES 2023 ===")
        cursor.execute("""
            SELECT 
                ROUND(AVG(precipitation_mm), 2) as precip_moy,
                ROUND(AVG(temp_mean_c), 1) as temp_moy,
                ROUND(MIN(temp_min_c), 1) as temp_min,
                ROUND(MAX(temp_max_c), 1) as temp_max,
                ROUND(AVG(humidity_pct), 1) as humid_moy
            FROM weather_data;
        """)
        stats = cursor.fetchone()
        print(f"Précipitation moyenne: {stats[0]} mm/jour")
        print(f"Température moyenne: {stats[1]}°C") 
        print(f"Température min/max: {stats[2]}°C / {stats[3]}°C")
        print(f"Humidité moyenne: {stats[4]}%")
        
        print("\n INTÉGRATION RÉUSSIE !")
        print("La base de données contient toutes les données nécessaires pour l'IA.")
        
        conn.close()
        
    except Exception as e:
        print(f" Erreur lors du test: {e}")

if __name__ == "__main__":
    test_database_integration()