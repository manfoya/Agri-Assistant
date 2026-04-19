"""Modele pour la table weather_data.

Donnees meteorologiques journalieres pour un point GPS.
Collectees depuis l'API NASA POWER (20 variables).
"""

from sqlalchemy import Column, Float, Text, PrimaryKeyConstraint

from api.core.database import Base


class WeatherData(Base):
    """Donnees meteo quotidiennes en un point (latitude, longitude, date)."""

    __tablename__ = "weather_data"

    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    date = Column(Text, nullable=False)

    # -- Precipitations --
    precipitation_mm = Column(Float, doc="Precipitations corrigees, mm/jour")

    # -- Temperatures --
    temp_mean_c = Column(Float, doc="Temperature moyenne a 2m, en degres C")
    temp_min_c = Column(Float, doc="Temperature minimale, degres C")
    temp_max_c = Column(Float, doc="Temperature maximale, degres C")
    temp_range_c = Column(Float, doc="Amplitude thermique du jour, degres C")
    temp_dew_c = Column(Float, doc="Temperature du point de rosee, degres C")
    temp_surface_c = Column(Float, doc="Temperature de surface, degres C")
    temp_wet_bulb = Column(Float, doc="Temperature thermometre mouille, degres C")

    # -- Humidite --
    humidity_pct = Column(Float, doc="Humidite relative a 2m, en pourcent")
    humidity_specific = Column(Float, doc="Humidite specifique, kg/kg")

    # -- Vent --
    wind_speed_2m = Column(Float, doc="Vitesse du vent a 2m, m/s")
    wind_speed_10m = Column(Float, doc="Vitesse du vent a 10m, m/s")
    wind_speed_50m = Column(Float, doc="Vitesse du vent a 50m, m/s")
    wind_direction_2m = Column(Float, doc="Direction du vent a 2m, degres")
    wind_direction_10m = Column(Float, doc="Direction du vent a 10m, degres")

    # -- Pression --
    pressure_kpa = Column(Float, doc="Pression de surface, kPa")

    # -- Rayonnement --
    solar_radiation = Column(Float, doc="Rayonnement solaire global, MJ/m2/jour")
    solar_clear_sky = Column(Float, doc="Rayonnement par ciel clair, MJ/m2/jour")
    solar_diffuse = Column(Float, doc="Rayonnement diffus, MJ/m2/jour")
    longwave_radiation = Column(Float, doc="Rayonnement infrarouge, MJ/m2/jour")

    __table_args__ = (
        PrimaryKeyConstraint("latitude", "longitude", "date"),
    )

    def __repr__(self) -> str:
        return f"<WeatherData lat={self.latitude} lon={self.longitude} date={self.date}>"
