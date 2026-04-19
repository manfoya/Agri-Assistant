"""Remplissage de la table crop_requirements.

Ce script insere les exigences agronomiques des 10 cultures cibles
dans la base de donnees SQLite. Les valeurs viennent de :
- FAO (Food and Agriculture Organization)
- IITA (International Institute of Tropical Agriculture)
- INRAB (Institut National des Recherches Agricoles du Benin)
- Litterature scientifique sur l'agriculture tropicale

Usage :
    python -m scripts.seed_crop_requirements
"""

import sys
import os

# Ajouter le dossier racine au path pour pouvoir importer api.*
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.core.database import engine, Base, SessionLocal
from api.models.crop_requirement import CropRequirement


# Les 10 cultures cibles avec leurs exigences agronomiques.
# Chaque dictionnaire represente une culture.
# Les valeurs "ideal" sont la plage optimale, les valeurs "min/max" sont
# les limites tolerees au-dela desquelles la plante souffre.
CROP_DATA = [
    {
        "name": "Mais",
        "scientific_name": "Zea mays",
        "category": "Cereale",
        # Sol
        "ph_min": 5.0, "ph_max": 8.0, "ph_ideal_min": 5.5, "ph_ideal_max": 7.5,
        "nitrogen_min": 1.0, "nitrogen_ideal": 2.5,
        "sand_max": 80.0, "clay_max": 45.0,
        # Climat
        "temp_min": 10.0, "temp_max": 40.0, "temp_ideal_min": 25.0, "temp_ideal_max": 30.0,
        "rainfall_min_mm": 500.0, "rainfall_max_mm": 1200.0,
        "rainfall_ideal_min_mm": 600.0, "rainfall_ideal_max_mm": 900.0,
        "humidity_min": 50.0, "humidity_max": 85.0,
        # Cycle
        "cycle_days_min": 90, "cycle_days_max": 120,
        "solar_radiation_min": 15.0,
    },
    {
        "name": "Manioc",
        "scientific_name": "Manihot esculenta",
        "category": "Tubercule",
        "ph_min": 4.5, "ph_max": 8.0, "ph_ideal_min": 5.5, "ph_ideal_max": 6.5,
        "nitrogen_min": 0.5, "nitrogen_ideal": 1.5,
        "sand_max": 85.0, "clay_max": 40.0,
        "temp_min": 15.0, "temp_max": 40.0, "temp_ideal_min": 25.0, "temp_ideal_max": 29.0,
        "rainfall_min_mm": 500.0, "rainfall_max_mm": 1500.0,
        "rainfall_ideal_min_mm": 800.0, "rainfall_ideal_max_mm": 1200.0,
        "humidity_min": 50.0, "humidity_max": 90.0,
        "cycle_days_min": 240, "cycle_days_max": 365,
        "solar_radiation_min": 14.0,
    },
    {
        "name": "Sorgho",
        "scientific_name": "Sorghum bicolor",
        "category": "Cereale",
        "ph_min": 5.0, "ph_max": 8.5, "ph_ideal_min": 5.5, "ph_ideal_max": 7.5,
        "nitrogen_min": 0.8, "nitrogen_ideal": 2.0,
        "sand_max": 85.0, "clay_max": 50.0,
        "temp_min": 12.0, "temp_max": 42.0, "temp_ideal_min": 25.0, "temp_ideal_max": 35.0,
        "rainfall_min_mm": 400.0, "rainfall_max_mm": 1000.0,
        "rainfall_ideal_min_mm": 500.0, "rainfall_ideal_max_mm": 800.0,
        "humidity_min": 40.0, "humidity_max": 80.0,
        "cycle_days_min": 100, "cycle_days_max": 140,
        "solar_radiation_min": 16.0,
    },
    {
        "name": "Mil",
        "scientific_name": "Pennisetum glaucum",
        "category": "Cereale",
        "ph_min": 5.0, "ph_max": 8.0, "ph_ideal_min": 5.5, "ph_ideal_max": 7.0,
        "nitrogen_min": 0.5, "nitrogen_ideal": 1.5,
        "sand_max": 90.0, "clay_max": 35.0,
        "temp_min": 15.0, "temp_max": 45.0, "temp_ideal_min": 28.0, "temp_ideal_max": 35.0,
        "rainfall_min_mm": 250.0, "rainfall_max_mm": 700.0,
        "rainfall_ideal_min_mm": 350.0, "rainfall_ideal_max_mm": 550.0,
        "humidity_min": 30.0, "humidity_max": 70.0,
        "cycle_days_min": 75, "cycle_days_max": 100,
        "solar_radiation_min": 18.0,
    },
    {
        "name": "Riz",
        "scientific_name": "Oryza sativa",
        "category": "Cereale",
        "ph_min": 4.5, "ph_max": 7.5, "ph_ideal_min": 5.5, "ph_ideal_max": 6.5,
        "nitrogen_min": 1.5, "nitrogen_ideal": 3.0,
        "sand_max": 60.0, "clay_max": 60.0,
        "temp_min": 15.0, "temp_max": 38.0, "temp_ideal_min": 22.0, "temp_ideal_max": 30.0,
        "rainfall_min_mm": 900.0, "rainfall_max_mm": 2000.0,
        "rainfall_ideal_min_mm": 1000.0, "rainfall_ideal_max_mm": 1500.0,
        "humidity_min": 60.0, "humidity_max": 95.0,
        "cycle_days_min": 120, "cycle_days_max": 150,
        "solar_radiation_min": 14.0,
    },
    {
        "name": "Niebe",
        "scientific_name": "Vigna unguiculata",
        "category": "Legumineuse",
        "ph_min": 5.5, "ph_max": 8.0, "ph_ideal_min": 6.0, "ph_ideal_max": 7.0,
        "nitrogen_min": 0.3, "nitrogen_ideal": 1.0,
        "sand_max": 85.0, "clay_max": 40.0,
        "temp_min": 15.0, "temp_max": 40.0, "temp_ideal_min": 25.0, "temp_ideal_max": 35.0,
        "rainfall_min_mm": 300.0, "rainfall_max_mm": 700.0,
        "rainfall_ideal_min_mm": 400.0, "rainfall_ideal_max_mm": 600.0,
        "humidity_min": 40.0, "humidity_max": 80.0,
        "cycle_days_min": 60, "cycle_days_max": 90,
        "solar_radiation_min": 16.0,
    },
    {
        "name": "Arachide",
        "scientific_name": "Arachis hypogaea",
        "category": "Legumineuse",
        "ph_min": 5.0, "ph_max": 7.5, "ph_ideal_min": 5.5, "ph_ideal_max": 6.5,
        "nitrogen_min": 0.5, "nitrogen_ideal": 1.2,
        "sand_max": 85.0, "clay_max": 35.0,
        "temp_min": 15.0, "temp_max": 40.0, "temp_ideal_min": 25.0, "temp_ideal_max": 30.0,
        "rainfall_min_mm": 500.0, "rainfall_max_mm": 900.0,
        "rainfall_ideal_min_mm": 550.0, "rainfall_ideal_max_mm": 750.0,
        "humidity_min": 50.0, "humidity_max": 80.0,
        "cycle_days_min": 90, "cycle_days_max": 130,
        "solar_radiation_min": 16.0,
    },
    {
        "name": "Coton",
        "scientific_name": "Gossypium hirsutum",
        "category": "Culture de rente",
        "ph_min": 5.5, "ph_max": 8.0, "ph_ideal_min": 6.0, "ph_ideal_max": 7.5,
        "nitrogen_min": 1.0, "nitrogen_ideal": 2.5,
        "sand_max": 75.0, "clay_max": 45.0,
        "temp_min": 15.0, "temp_max": 42.0, "temp_ideal_min": 25.0, "temp_ideal_max": 35.0,
        "rainfall_min_mm": 700.0, "rainfall_max_mm": 1300.0,
        "rainfall_ideal_min_mm": 800.0, "rainfall_ideal_max_mm": 1100.0,
        "humidity_min": 50.0, "humidity_max": 80.0,
        "cycle_days_min": 150, "cycle_days_max": 180,
        "solar_radiation_min": 17.0,
    },
    {
        "name": "Igname",
        "scientific_name": "Dioscorea spp.",
        "category": "Tubercule",
        "ph_min": 5.0, "ph_max": 7.5, "ph_ideal_min": 5.5, "ph_ideal_max": 6.5,
        "nitrogen_min": 1.0, "nitrogen_ideal": 2.5,
        "sand_max": 70.0, "clay_max": 40.0,
        "temp_min": 18.0, "temp_max": 38.0, "temp_ideal_min": 25.0, "temp_ideal_max": 30.0,
        "rainfall_min_mm": 1000.0, "rainfall_max_mm": 1800.0,
        "rainfall_ideal_min_mm": 1100.0, "rainfall_ideal_max_mm": 1500.0,
        "humidity_min": 60.0, "humidity_max": 90.0,
        "cycle_days_min": 240, "cycle_days_max": 300,
        "solar_radiation_min": 14.0,
    },
    {
        "name": "Soja",
        "scientific_name": "Glycine max",
        "category": "Legumineuse",
        "ph_min": 5.5, "ph_max": 7.5, "ph_ideal_min": 6.0, "ph_ideal_max": 7.0,
        "nitrogen_min": 0.5, "nitrogen_ideal": 1.5,
        "sand_max": 75.0, "clay_max": 45.0,
        "temp_min": 15.0, "temp_max": 38.0, "temp_ideal_min": 20.0, "temp_ideal_max": 30.0,
        "rainfall_min_mm": 450.0, "rainfall_max_mm": 900.0,
        "rainfall_ideal_min_mm": 500.0, "rainfall_ideal_max_mm": 700.0,
        "humidity_min": 50.0, "humidity_max": 85.0,
        "cycle_days_min": 100, "cycle_days_max": 130,
        "solar_radiation_min": 15.0,
    },
]


def seed_crop_requirements():
    """Insere ou met a jour les 10 cultures dans la BDD.

    Si une culture existe deja (meme nom), elle est ecrasee.
    """
    # Creer la table si elle n'existe pas
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        for crop_dict in CROP_DATA:
            # Verifier si la culture existe deja
            existing = db.query(CropRequirement).filter_by(
                name=crop_dict["name"]
            ).first()

            if existing:
                # Mise a jour de chaque champ
                for key, value in crop_dict.items():
                    setattr(existing, key, value)
                print(f"  Mise a jour : {crop_dict['name']}")
            else:
                # Nouvelle insertion
                db.add(CropRequirement(**crop_dict))
                print(f"  Ajout : {crop_dict['name']}")

        db.commit()
        print(f"\n{len(CROP_DATA)} cultures inserees/mises a jour avec succes.")
    except Exception as error:
        db.rollback()
        print(f"Erreur : {error}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_crop_requirements()
