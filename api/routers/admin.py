from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import func

from api.core.database import get_db
from api.models.recommendation import RecommendationLog

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/", response_class=HTMLResponse)
def get_admin_dashboard(db: Session = Depends(get_db)):
    """Affiche le dashboard d'administration riche avec les statistiques."""
    
    # Statistiques globales
    total_searches = db.query(RecommendationLog).count()
    
    # Top cultures recommandees (Top 1)
    top_crops = db.query(
        RecommendationLog.crop_1, 
        func.count(RecommendationLog.crop_1).label('count')
    ).group_by(RecommendationLog.crop_1).order_by(func.count(RecommendationLog.crop_1).desc()).limit(5).all()
    
    # Distribution des types de sol
    soil_distribution = db.query(
        RecommendationLog.soil_type,
        func.count(RecommendationLog.soil_type).label('count')
    ).group_by(RecommendationLog.soil_type).order_by(func.count(RecommendationLog.soil_type).desc()).limit(5).all()

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
            .container {{ max-width: 1000px; margin: 0 auto; }}
            h1 {{ color: #10b981; border-bottom: 2px solid #1e293b; padding-bottom: 20px; }}
            .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 24px; margin-top: 40px; }}
            .card {{ background: #1e293b; border-radius: 16px; padding: 24px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
            .stat-value {{ font-size: 48px; font-weight: 800; color: #10b981; margin: 10px 0; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #334155; }}
            th {{ color: #94a3b8; font-weight: 600; }}
            .badge {{ background: rgba(59, 130, 246, 0.2); color: #60a5fa; padding: 4px 8px; border-radius: 4px; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🌿 Agri-Assistant | Centre de Controle</h1>
            
            <div class="grid">
                <!-- KPI -->
                <div class="card">
                    <h3>Total des Analyses GPS</h3>
                    <div class="stat-value">{total_searches}</div>
                    <p style="color: #94a3b8;">Requetes depuis le lancement</p>
                </div>

                <!-- Palmares Cultures -->
                <div class="card">
                    <h3>🏆 Top 5 Cultures Recommandees</h3>
                    <table>
                        <tr><th>Culture</th><th>Occurrences</th></tr>
                        {''.join(f"<tr><td><strong>{c[0]}</strong></td><td><span class='badge'>{c[1]} fois</span></td></tr>" for c in top_crops if c[0])}
                    </table>
                </div>

                <!-- Types de Sol -->
                <div class="card">
                    <h3>🌍 Sols les plus frequents</h3>
                    <table>
                        <tr><th>Type de Sol</th><th>Analyses</th></tr>
                        {''.join(f"<tr><td>{s[0]}</td><td><span class='badge'>{s[1]}</span></td></tr>" for s in soil_distribution if s[0])}
                    </table>
                </div>
            </div>
            
            <div style="margin-top: 50px; color: #64748b; font-size: 14px; text-align: center;">
                Concu pour l'analytique anonymisee • Agri-Assistant 2026
            </div>
        </div>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)
