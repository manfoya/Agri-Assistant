"""Algorithme de Matching Agronomique.

Ce service est le "cerveau" de l'application. Il prend les donnees
exactes du sol et du climat d'un point GPS, et calcule un score
de compatibilite (0 a 100%) pour chaque culture de notre base.
"""

from typing import Dict, Any, List
from datetime import datetime

from api.models.crop_requirement import CropRequirement
from api.schemas.recommendation import CropRecommendation, SowingWindow

# Poids extraits de l'analyse Kaggle + expertise agronomique (Total = 1.0)
WEIGHTS = {
    "rainfall": 0.25,     # L'eau est le facteur limitant numero 1
    "humidity": 0.10,
    "temperature": 0.10,
    "nitrogen": 0.15,     # Macronutriment principal
    "ph": 0.10,
    "soc": 0.10,          # Carbone organique (retention d'eau/nutriments)
    "cec": 0.05,          # Capacite d'echange (proxy pour P et K)
    "texture": 0.15       # Sable/Argile (physique du sol)
}

def calculate_partial_score(value: float, min_val: float, max_val: float, ideal_min: float, ideal_max: float) -> float:
    """Calcule un score sur 100 pour un parametre donne (ex: pH).
    
    - Si la valeur est dans la plage ideale : 100%
    - Si elle est hors des limites absolues (min/max) : 0%
    - Si elle est entre la limite absolue et l'ideal : score progressif
    """
    if value < min_val or value > max_val:
        return 0.0
    
    if ideal_min <= value <= ideal_max:
        return 100.0
        
    # Calcul progressif si on est en dessous de l'ideal
    if value < ideal_min:
        return ((value - min_val) / (ideal_min - min_val)) * 100.0
        
    # Calcul progressif si on est au-dessus de l'ideal
    if value > ideal_max:
        return ((max_val - value) / (max_val - ideal_max)) * 100.0
        
    return 0.0

def evaluate_crop(crop: CropRequirement, soil_data: Dict[str, Any], climate_data: Dict[str, Any]) -> tuple[float, List[str]]:
    """Evalue a quel point un environnement correspond a une culture.
    
    Retourne le score final (0 a 100) et la liste des points forts/faibles.
    """
    reasons = []
    
    # 1. Eau (Pluie + Humidite)
    rainfall_score = calculate_partial_score(
        climate_data["rainfall_annual_mm"],
        crop.rainfall_min_mm, crop.rainfall_max_mm,
        crop.rainfall_ideal_min_mm, crop.rainfall_ideal_max_mm
    )
    humidity_score = calculate_partial_score(
        climate_data["humidity_pct"],
        crop.humidity_min, crop.humidity_max,
        crop.humidity_min + 10, crop.humidity_max - 10  # Ideals approximatifs
    )
    
    # 2. Climat (Temperature)
    temp_score = calculate_partial_score(
        climate_data["temp_mean_c"],
        crop.temp_min, crop.temp_max,
        crop.temp_ideal_min, crop.temp_ideal_max
    )
    
    # 3. Chimie du sol (Azote, pH, SOC, CEC)
    n_score = calculate_partial_score(soil_data.get("nitrogen", 0), 0, 5, crop.nitrogen_min, crop.nitrogen_ideal)
    ph_score = calculate_partial_score(soil_data.get("ph", 6), crop.ph_min, crop.ph_max, crop.ph_ideal_min, crop.ph_ideal_max)
    
    # Pour SOC et CEC, on n'a pas de limites strictes par plante, on evalue la qualite absolue
    soc = soil_data.get("soc", 10)
    soc_score = min(100.0, (soc / 20.0) * 100.0) # > 20 g/kg = 100%
    
    cec = soil_data.get("cec", 10)
    cec_score = min(100.0, (cec / 15.0) * 100.0) # > 15 cmol/kg = 100%
    
    # 4. Physique du sol (Texture)
    sand = soil_data.get("sand", 50)
    clay = soil_data.get("clay", 20)
    texture_score = 100.0
    if sand > crop.sand_max:
        texture_score -= (sand - crop.sand_max) * 2
    if clay > crop.clay_max:
        texture_score -= (clay - crop.clay_max) * 2
    texture_score = max(0.0, texture_score)
    
    # --- Calcul final pondeere ---
    final_score = (
        (rainfall_score * WEIGHTS["rainfall"]) +
        (humidity_score * WEIGHTS["humidity"]) +
        (temp_score * WEIGHTS["temperature"]) +
        (n_score * WEIGHTS["nitrogen"]) +
        (ph_score * WEIGHTS["ph"]) +
        (soc_score * WEIGHTS["soc"]) +
        (cec_score * WEIGHTS["cec"]) +
        (texture_score * WEIGHTS["texture"])
    )
    
    # --- Generation des explications ---
    if rainfall_score > 80:
        reasons.append("Pluviometrie ideale pour la plante.")
    elif rainfall_score < 40:
        reasons.append("Attention : La zone manque de pluie pour cette culture.")
        
    if ph_score > 80:
        reasons.append("Le pH du sol est parfaitement adapte.")
    
    if texture_score < 50:
        reasons.append("La texture du sol (Sable/Argile) n'est pas optimale.")
        
    return final_score, reasons

def get_contextual_advice(crop: CropRequirement) -> str:
    """Genere le conseil contextuel base sur la date du jour et le cycle."""
    current_month = datetime.now().strftime("%B") # Ex: 'April'
    # Traduction simple pour le prototype
    mois_fr = {
        "January": "Janvier", "February": "Fevrier", "March": "Mars",
        "April": "Avril", "May": "Mai", "June": "Juin",
        "July": "Juillet", "August": "Aout", "September": "Septembre",
        "October": "Octobre", "November": "Novembre", "December": "Decembre"
    }
    mois_actuel = mois_fr.get(current_month, current_month)
    
    duree = crop.cycle_days_min
    
    return f"Nous sommes en {mois_actuel}. Cette plante necessite un cycle de {duree} jours. Prevoyez l'eau en consequence."

def run_matching(soil_data: Dict[str, Any], climate_data: Dict[str, Any], all_crops: List[CropRequirement]) -> List[CropRecommendation]:
    """Execute l'algorithme sur toutes les cultures et renvoie le top 3."""
    results = []
    
    for crop in all_crops:
        score, reasons = evaluate_crop(crop, soil_data, climate_data)
        
        # On ne garde que les plantes qui ont au moins 20% de compatibilite
        if score > 20.0:
            advice = get_contextual_advice(crop)
            reasons.append(advice)
            
            results.append({
                "crop": crop.name,
                "confidence": round(score / 100.0, 2), # Convertir en ratio 0-1
                "reasons": reasons
            })
            
    # Trier par score decroissant
    results.sort(key=lambda x: x["confidence"], reverse=True)
    
    # Formater en schema Pydantic pour l'API (Top 3)
    recommendations = []
    for i, res in enumerate(results[:3]):
        recommendations.append(
            CropRecommendation(
                rank=i + 1,
                crop=res["crop"],
                confidence=res["confidence"],
                reasons=res["reasons"],
                sowing_window=None # Simplifie selon la nouvelle logique
            )
        )
        
    return recommendations
