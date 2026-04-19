"""Modele pour la table crop_requirements.

Contient les exigences agronomiques de chaque culture :
plages ideales de sol, climat, et cycle de croissance.
Ces donnees servent de reference pour l'algorithme de matching.
"""

from sqlalchemy import Column, Integer, Float, Text

from api.core.database import Base


class CropRequirement(Base):
    """Exigences agronomiques d'une culture.

    Chaque ligne represente une culture avec ses plages ideales
    pour le sol, le climat, et ses caracteristiques de cycle.
    """

    __tablename__ = "crop_requirements"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # -- Identification --
    name = Column(Text, nullable=False, unique=True, doc="Nom commun")
    scientific_name = Column(Text, doc="Nom scientifique latin")
    category = Column(Text, doc="Cereale, Legumineuse, Tubercule, etc.")

    # -- Exigences de sol : plages ideales (min/max) --
    ph_min = Column(Float, doc="pH minimum tolere")
    ph_max = Column(Float, doc="pH maximum tolere")
    ph_ideal_min = Column(Float, doc="pH ideal bas")
    ph_ideal_max = Column(Float, doc="pH ideal haut")

    nitrogen_min = Column(Float, doc="Azote minimum necessaire, g/kg")
    nitrogen_ideal = Column(Float, doc="Azote ideal, g/kg")

    # Texture du sol : tolerance
    sand_max = Column(Float, doc="Pourcentage de sable maximum tolere")
    clay_max = Column(Float, doc="Pourcentage d'argile maximum tolere")

    # -- Exigences climatiques --
    temp_min = Column(Float, doc="Temperature minimale toleree, degres C")
    temp_max = Column(Float, doc="Temperature maximale toleree, degres C")
    temp_ideal_min = Column(Float, doc="Temperature ideale basse, degres C")
    temp_ideal_max = Column(Float, doc="Temperature ideale haute, degres C")

    rainfall_min_mm = Column(Float, doc="Precipitations minimales pour le cycle, mm")
    rainfall_max_mm = Column(Float, doc="Precipitations maximales tolerees, mm")
    rainfall_ideal_min_mm = Column(Float, doc="Precipitations ideales basses, mm")
    rainfall_ideal_max_mm = Column(Float, doc="Precipitations ideales hautes, mm")

    humidity_min = Column(Float, doc="Humidite relative minimum, pourcent")
    humidity_max = Column(Float, doc="Humidite relative maximum, pourcent")

    # -- Cycle de croissance --
    cycle_days_min = Column(Integer, doc="Duree minimale du cycle, jours")
    cycle_days_max = Column(Integer, doc="Duree maximale du cycle, jours")

    # -- Besoins en lumiere --
    solar_radiation_min = Column(Float, doc="Rayonnement solaire minimum, MJ/m2/jour")

    def __repr__(self) -> str:
        return f"<CropRequirement name={self.name}>"
