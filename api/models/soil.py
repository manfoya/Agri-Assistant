"""Modele pour la table soil_data.

Represente les proprietes physico-chimiques du sol
en un point GPS donne. Les donnees viennent de l'API ISRIC SoilGrids.
"""

from sqlalchemy import Column, Float, PrimaryKeyConstraint

from api.core.database import Base


class SoilData(Base):
    """Proprietes du sol pour une coordonnee (latitude, longitude)."""

    __tablename__ = "soil_data"

    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    # Texture du sol
    sand_pct = Column(Float, doc="Pourcentage de sable")
    clay_pct = Column(Float, doc="Pourcentage d'argile")

    # Chimie du sol
    ph = Column(Float, doc="pH du sol, mesure dans l'eau")
    soc_g_kg = Column(Float, doc="Carbone organique du sol, en g/kg")
    nitrogen_g_kg = Column(Float, doc="Azote total, en g/kg")
    cec_cmol_kg = Column(Float, doc="Capacite d'echange cationique, en cmol/kg")

    # Physique du sol
    bulk_density_kg_m3 = Column(Float, doc="Densite apparente, en kg/m3")

    __table_args__ = (
        PrimaryKeyConstraint("latitude", "longitude"),
    )

    def __repr__(self) -> str:
        return f"<SoilData lat={self.latitude} lon={self.longitude} ph={self.ph}>"

    def to_dict(self) -> dict:
        """Renvoie les colonnes sous forme de dictionnaire simple."""
        return {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "sand_pct": self.sand_pct,
            "clay_pct": self.clay_pct,
            "ph": self.ph,
            "soc_g_kg": self.soc_g_kg,
            "nitrogen_g_kg": self.nitrogen_g_kg,
            "cec_cmol_kg": self.cec_cmol_kg,
            "bulk_density_kg_m3": self.bulk_density_kg_m3,
        }
