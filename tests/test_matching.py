"""Tests pour l'algorithme de Matching Agronomique.

Permet de verifier que l'algorithme reagit bien aux variations
de sol et de climat pour attribuer le bon score.
"""

from api.models.crop_requirement import CropRequirement
from api.services.matching_service import evaluate_crop, calculate_partial_score

def test_calculate_partial_score():
    # Cas 1 : Dans l'ideal (score 100)
    assert calculate_partial_score(6.0, 5.0, 8.0, 5.5, 7.5) == 100.0
    
    # Cas 2 : Hors limite (score 0)
    assert calculate_partial_score(4.0, 5.0, 8.0, 5.5, 7.5) == 0.0
    
    # Cas 3 : Entre min et ideal_min (score partiel)
    # 5.25 est exactement a mi-chemin entre 5.0 (min) et 5.5 (ideal_min) -> 50%
    assert calculate_partial_score(5.25, 5.0, 8.0, 5.5, 7.5) == 50.0

def test_evaluate_crop_maize():
    """Teste le calcul pour le Mais avec des conditions parfaites puis mauvaises."""
    maize = CropRequirement(
        name="Mais",
        ph_min=5.0, ph_max=8.0, ph_ideal_min=5.5, ph_ideal_max=7.5,
        nitrogen_min=1.0, nitrogen_ideal=2.5,
        sand_max=80.0, clay_max=45.0,
        temp_min=10.0, temp_max=40.0, temp_ideal_min=25.0, temp_ideal_max=30.0,
        rainfall_min_mm=500.0, rainfall_max_mm=1200.0,
        rainfall_ideal_min_mm=600.0, rainfall_ideal_max_mm=900.0,
        humidity_min=50.0, humidity_max=85.0,
        cycle_days_min=120
    )
    
    # Conditions parfaites
    perfect_soil = {"ph": 6.5, "nitrogen": 2.5, "sand": 50, "clay": 20, "soc": 25, "cec": 20}
    perfect_climate = {
        "temp_mean_c": 28.0, "rainfall_annual_mm": 800.0, "humidity_pct": 70.0,
        "monthly_temp": {m: 28.0 for m in ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]},
        # Pour le Mais (env 4 mois), on veut au moins 600mm, donc env 150mm par mois = 5mm par jour
        "monthly_precip": {m: 5.0 for m in ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]},
        "monthly_humidity": {m: 70.0 for m in ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]}
    }
    
    score_perfect, reasons = evaluate_crop(maize, perfect_soil, perfect_climate)
    assert score_perfect == 100.0
    assert "Pluviometrie ideale pour la plante." in reasons
    
    # Conditions arides (trop sec, ph extreme)
    arid_soil = {"ph": 4.5, "nitrogen": 0.5, "sand": 90, "clay": 5, "soc": 5, "cec": 5}
    arid_climate = {
        "temp_mean_c": 42.0, "rainfall_annual_mm": 300.0, "humidity_pct": 20.0,
        "monthly_temp": {m: 42.0 for m in ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]},
        "monthly_precip": {m: 0.5 for m in ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]},
        "monthly_humidity": {m: 20.0 for m in ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]}
    }
    
    score_arid, reasons_arid = evaluate_crop(maize, arid_soil, arid_climate)
    assert score_arid < 30.0 # Score tres bas attendu
