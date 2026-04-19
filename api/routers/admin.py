from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime

from api.core.database import get_db
from api.models.recommendation import RecommendationLog

router = APIRouter(prefix="/admin", tags=["Admin"])

def get_region(lat: float) -> str:
    """Determine la region du Benin en fonction de la latitude."""
    if lat >= 9.5:
        return "Nord"
    elif lat >= 7.5:
        return "Centre"
    else:
        return "Sud"

def get_acidity_label(ph: float) -> str:
    if ph < 5.5:
        return "tres acides"
    elif ph < 6.5:
        return "legerement acides"
    elif ph <= 7.5:
        return "neutres"
    else:
        return "basiques"

@router.get("/", response_class=HTMLResponse)
def get_admin_dashboard(db: Session = Depends(get_db)):
    """Affiche le dashboard d'administration riche avec les statistiques avancees."""
    
    logs = db.query(RecommendationLog).all()
    total_searches = len(logs)
    
    # Textes des insights en langage naturel
    region_insight = "Pas assez de donnees pour la repartition regionale."
    crop_insight = "Pas assez de donnees pour les tendances de ce mois."
    soil_insight = "Pas assez de donnees pour l'analyse des sols."

    if total_searches > 0:
        # 1. Repartition Geographique
        regions = {"Nord": 0, "Centre": 0, "Sud": 0}
        for log in logs:
            regions[get_region(log.latitude)] += 1
            
        top_region = max(regions, key=regions.get)
        top_region_pct = int((regions[top_region] / total_searches) * 100)
        region_insight = f"📍 <strong>{top_region_pct}%</strong> de nos utilisateurs se trouvent dans le <strong>{top_region} du Benin</strong>."

        # 2. Tendance mensuelle
        current_month = datetime.utcnow().month
        current_year = datetime.utcnow().year
        monthly_logs = [log for log in logs if log.requested_at.month == current_month and log.requested_at.year == current_year]
        
        if monthly_logs:
            crop_counts = {}
            for log in monthly_logs:
                if log.crop_1:
                    crop_counts[log.crop_1] = crop_counts.get(log.crop_1, 0) + 1
            
            if crop_counts:
                top_crop = max(crop_counts, key=crop_counts.get)
                top_crop_count = crop_counts[top_crop]
                
                # Trouver la culture la moins recommandee ou prendre une comparaison arbitraire si 1 seule culture
                other_crops = [c for c in crop_counts if c != top_crop]
                if other_crops:
                    worst_crop = min(other_crops, key=lambda k: crop_counts[k])
                    worst_crop_count = crop_counts[worst_crop]
                    crop_insight = f"🌾 Le <strong>{top_crop}</strong> a ete recommande <strong>{top_crop_count} fois</strong> ce mois-ci, contre seulement {worst_crop_count} fois pour le {worst_crop}."
                else:
                    crop_insight = f"🌾 Le <strong>{top_crop}</strong> a ete exclusif ce mois-ci avec <strong>{top_crop_count} recommandations</strong>."

        # 3. Acidite des sols par region phare
        region_phs = [log.ph for log in logs if get_region(log.latitude) == top_region and log.ph is not None]
        if region_phs:
            avg_ph = sum(region_phs) / len(region_phs)
            acidity = get_acidity_label(avg_ph)
            soil_insight = f"🧪 La majorite des sols analyses dans la region <strong>{top_region}</strong> sont <strong>{acidity}</strong> (pH moyen: {avg_ph:.1f})."

    # Generer le HTML (design minimaliste mais riche en info)
    html_content = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Dashboard Admin | Agri-Assistant</title>
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap" rel="stylesheet">
        <style>
            body {{ font-family: 'Outfit', sans-serif; background-color: #0f172a; color: #f8fafc; margin: 0; padding: 40px; }}
            .container {{ max-width: 900px; margin: 0 auto; }}
            h1 {{ color: #10b981; border-bottom: 2px solid #1e293b; padding-bottom: 20px; }}
            .insights-container {{ background: #1e293b; border-radius: 16px; padding: 32px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-top: 40px; }}
            .insight-box {{ background: rgba(16, 185, 129, 0.05); border-left: 4px solid #10b981; padding: 20px; margin-bottom: 24px; border-radius: 0 8px 8px 0; font-size: 18px; line-height: 1.6; }}
            .insight-box:last-child {{ margin-bottom: 0; }}
            .stat-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; }}
            .total-badge {{ background: #10b981; color: white; padding: 8px 16px; border-radius: 20px; font-weight: bold; font-size: 20px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="stat-header">
                <h1>🌿 Agri-Assistant | Intelligence Artificielle & Data</h1>
                <div class="total-badge">{total_searches} Analyses Globales</div>
            </div>
            
            <p style="color: #94a3b8; font-size: 18px;">Bienvenue sur le tableau de bord analytique. Voici ce que les donnees de terrain nous apprennent :</p>
            
            <div class="insights-container">
                <div class="insight-box">
                    {region_insight}
                </div>
                
                <div class="insight-box">
                    {crop_insight}
                </div>
                
                <div class="insight-box">
                    {soil_insight}
                </div>
            </div>
            
            <div style="margin-top: 50px; color: #64748b; font-size: 14px; text-align: center;">
                Generateur d'Insights en Langage Naturel • Agri-Assistant 2026
            </div>
        </div>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)
