# On charge les librairies
library(nasapower)
library(RSQLite)
library(dplyr)

# ==============================================================================
# FONCTION DE RÉCUPÉRATION DE DONNÉES MÉTÉO - NASA POWER
# ==============================================================================
get_weather_data <- function(lon, lat, start_date, end_date) {
  cat("... Récupération des données météo depuis NASA POWER\n")

  # Récupérer les données météo
  weather_data <- get_power(
    community = "ag",  # Données agricoles
    lonlat = c(lon, lat),
    dates = c(start_date, end_date),
    temporal_api = "daily",
    pars = c(
      "PRECTOTCORR",    # Précipitations corrigées (mm/jour)
      "T2M",            # Température moyenne à 2m (°C)
      "T2M_MIN",        # Température minimale (°C)
      "T2M_MAX",        # Température maximale (°C)
      "T2M_RANGE",      # Amplitude thermique quotidienne (°C)
      "T2MDEW",         # Température du point de rosée (°C)
      "TS",             # Température de surface (°C)
      "RH2M",           # Humidité relative à 2m (%)
      "QV2M",           # Humidité spécifique (kg/kg)
      "WS2M",           # Vitesse du vent à 2m (m/s)
      "WS10M",          # Vitesse du vent à 10m (m/s)
      "WD2M",           # Direction du vent à 2m (degrés)
      "PS",             # Pression de surface (kPa)
      "ALLSKY_SFC_SW_DWN",   # Rayonnement solaire global (MJ/m²/jour)
      "CLRSKY_SFC_SW_DWN",   # Rayonnement par ciel clair (MJ/m²/jour)
      "ALLSKY_SFC_SW_DIFF",  # Rayonnement diffus (MJ/m²/jour)
      "ALLSKY_SFC_LW_DWN",   # Rayonnement infrarouge (MJ/m²/jour)
      "T2MWET",              # Température thermomètre mouillé (°C)
      "WS50M",               # Vitesse du vent à 50m (m/s)
      "WD10M"                # Direction du vent à 10m (degrés)
    )
  )
  
  return(weather_data)
}

# ==============================================================================
# SCRIPT POUR RÉCUPÉRATION DES DONNÉES : ETL (Extract, Transform, Load)
# ==============================================================================

# On configure les paramètres de la récupération (lat, lon, dates, chemin BDD)
target_lat <- 7.15
target_lon <- 2.05
start_date <- "2023-01-01"
end_date <- "2023-12-31"  # Test avec 1 an seulement pour simplifier
db_path <- "data/agridata.sqlite"

# --- 1. EXTRACT : Récupération des données avec notre fonction ---
cat("Étape 1: Récupération des données météo...\n")
weather_data <- get_weather_data(target_lon, target_lat, start_date, end_date)
cat("-> Données récupérées avec succès.\n\n")

# --- DEBUG : Examiner la structure des données ---
cat("DEBUG: Structure des données reçues:\n")
print(str(weather_data))
print(head(weather_data, 3))
cat("\n")

# --- 2. TRANSFORM : Nettoyage et formatage ---
cat("Étape 2: Formatage des données...\n")

weather_data_formatted <- weather_data %>%
  mutate(  # mutate pour ajouter/modifier des colonnes
    latitude = target_lat,
    longitude = target_lon,
    date = as.character(YYYYMMDD)
  ) %>%
  select(   # sélectionner toutes les colonnes nécessaires
    latitude, longitude, date,
    precipitation_mm = PRECTOTCORR,
    temp_mean_c = T2M,
    temp_min_c = T2M_MIN,
    temp_max_c = T2M_MAX,
    temp_range_c = T2M_RANGE,
    temp_dew_c = T2MDEW,
    temp_surface_c = TS,
    humidity_pct = RH2M,
    humidity_specific = QV2M,
    wind_speed_2m = WS2M,
    wind_speed_10m = WS10M,
    wind_direction_2m = WD2M,
    pressure_kpa = PS,
    solar_radiation = ALLSKY_SFC_SW_DWN,
    solar_clear_sky = CLRSKY_SFC_SW_DWN,
    solar_diffuse = ALLSKY_SFC_SW_DIFF,
    longwave_radiation = ALLSKY_SFC_LW_DWN,
    temp_wet_bulb = T2MWET,
    wind_speed_50m = WS50M,
    wind_direction_10m = WD10M
  )
cat("-> Données formatées avec succès.\n\n")

# --- 3. LOAD : Connexion et écriture dans la base de données ---
cat("Étape 3: Écriture dans la base de données SQLite...\n")
con <- dbConnect(RSQLite::SQLite(), db_path)

# Supprimer l'ancienne table si elle existe
dbExecute(con, "DROP TABLE IF EXISTS weather_data;")

# Créer la table si elle n'existe pas
dbExecute(con, "
CREATE TABLE IF NOT EXISTS weather_data (
  latitude REAL,
  longitude REAL,
  date TEXT NOT NULL,
  precipitation_mm REAL,
  temp_mean_c REAL,
  temp_min_c REAL,
  temp_max_c REAL,
  temp_range_c REAL,
  temp_dew_c REAL,
  temp_surface_c REAL,
  humidity_pct REAL,
  humidity_specific REAL,
  wind_speed_2m REAL,
  wind_speed_10m REAL,
  wind_direction_2m REAL,
  pressure_kpa REAL,
  solar_radiation REAL,
  solar_clear_sky REAL,
  solar_diffuse REAL,
  longwave_radiation REAL,
  temp_wet_bulb REAL,
  wind_speed_50m REAL,
  wind_direction_10m REAL,
  PRIMARY KEY (latitude, longitude, date)
);
")

# Insérer les données (avec 'ON CONFLICT DO UPDATE' pour éviter les doublons et mettre à jour)
query <- "INSERT INTO weather_data (latitude, longitude, date, precipitation_mm, temp_mean_c, temp_min_c, temp_max_c, temp_range_c, temp_dew_c, temp_surface_c, humidity_pct, humidity_specific, wind_speed_2m, wind_speed_10m, wind_direction_2m, pressure_kpa, solar_radiation, solar_clear_sky, solar_diffuse, longwave_radiation, temp_wet_bulb, wind_speed_50m, wind_direction_10m) 
          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
          ON CONFLICT(latitude, longitude, date) DO UPDATE SET 
            precipitation_mm = excluded.precipitation_mm,
            temp_mean_c = excluded.temp_mean_c,
            temp_min_c = excluded.temp_min_c,
            temp_max_c = excluded.temp_max_c,
            temp_range_c = excluded.temp_range_c,
            temp_dew_c = excluded.temp_dew_c,
            temp_surface_c = excluded.temp_surface_c,
            humidity_pct = excluded.humidity_pct,
            humidity_specific = excluded.humidity_specific,
            wind_speed_2m = excluded.wind_speed_2m,
            wind_speed_10m = excluded.wind_speed_10m,
            wind_direction_2m = excluded.wind_direction_2m,
            pressure_kpa = excluded.pressure_kpa,
            solar_radiation = excluded.solar_radiation,
            solar_clear_sky = excluded.solar_clear_sky,
            solar_diffuse = excluded.solar_diffuse,
            longwave_radiation = excluded.longwave_radiation,
            temp_wet_bulb = excluded.temp_wet_bulb,
            wind_speed_50m = excluded.wind_speed_50m,
            wind_direction_10m = excluded.wind_direction_10m;"

dbBegin(con)
# Insérer ligne par ligne avec les bonnes colonnes
for(i in 1:nrow(weather_data_formatted)) {
  row_data <- list(
    weather_data_formatted$latitude[i],
    weather_data_formatted$longitude[i], 
    weather_data_formatted$date[i],
    weather_data_formatted$precipitation_mm[i],
    weather_data_formatted$temp_mean_c[i],
    weather_data_formatted$temp_min_c[i],
    weather_data_formatted$temp_max_c[i],
    weather_data_formatted$temp_range_c[i],
    weather_data_formatted$temp_dew_c[i],
    weather_data_formatted$temp_surface_c[i],
    weather_data_formatted$humidity_pct[i],
    weather_data_formatted$humidity_specific[i],
    weather_data_formatted$wind_speed_2m[i],
    weather_data_formatted$wind_speed_10m[i],
    weather_data_formatted$wind_direction_2m[i],
    weather_data_formatted$pressure_kpa[i],
    weather_data_formatted$solar_radiation[i],
    weather_data_formatted$solar_clear_sky[i],
    weather_data_formatted$solar_diffuse[i],
    weather_data_formatted$longwave_radiation[i],
    weather_data_formatted$temp_wet_bulb[i],
    weather_data_formatted$wind_speed_50m[i],
    weather_data_formatted$wind_direction_10m[i]
  )
  dbExecute(con, query, params = row_data)
}
dbCommit(con)

cat(paste("->", nrow(weather_data_formatted), "lignes insérées/mises à jour dans", db_path, "\n\n"))

# Déconnexion
dbDisconnect(con)
cat("Opération terminée !\n")