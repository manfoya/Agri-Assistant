"""Modele pour la table recommendation_log.

Stocke l'historique des recommandations generees par l'API.
Utile pour analyser l'usage et ameliorer le modele plus tard.
"""

from datetime import datetime, timezone

from sqlalchemy import Column, Integer, Float, Text, DateTime

from api.core.database import Base


class RecommendationLog(Base):
    """Une ligne = une requete de recommandation faite par un utilisateur."""

    __tablename__ = "recommendation_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    requested_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Top 3 des cultures recommandees
    crop_1 = Column(Text, doc="Culture recommandee numero 1")
    confidence_1 = Column(Float, doc="Confiance pour la culture 1, entre 0 et 1")
    crop_2 = Column(Text, doc="Culture recommandee numero 2")
    confidence_2 = Column(Float, doc="Confiance pour la culture 2")
    crop_3 = Column(Text, doc="Culture recommandee numero 3")
    confidence_3 = Column(Float, doc="Confiance pour la culture 3")

    # Contexte geographique
    nearest_zone = Column(Text, doc="Zone agro-ecologique la plus proche")
    climate_type = Column(Text, doc="Type de climat de la zone")

    def __repr__(self) -> str:
        return f"<RecommendationLog id={self.id} crop_1={self.crop_1}>"
