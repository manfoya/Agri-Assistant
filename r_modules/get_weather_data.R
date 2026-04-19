# On charge les librairies
library(nasapower)
library(RSQLite)
library(dplyr)

# ==============================================================================
# FONCTION DE RECUPERATION DE DONNEES METEO - NASA POWER
# ==============================================================================
get_weather_data <- function(lon, lat, start_date, end_date) {
  # Recuperer les donnees meteo
  weather_data <- get_power(
    community = "ag",  # Donnees agricoles
    lonlat = c(lon, lat),
    dates = c(start_date, end_date),
    temporal_api = "daily",
    pars = c(
      "PRECTOTCORR",    # Precipitations corrigees (mm/jour)
      "T2M",            # Temperature moyenne a 2m (degC)
      "T2M_MIN",        # Temperature minimale (degC)
      "T2M_MAX",        # Temperature maximale (degC)
      "T2M_RANGE",      # Amplitude thermique quotidienne (degC)
      "T2MDEW",         # Temperature du point de rosee (degC)
      "TS",             # Temperature de surface (degC)
      "RH2M",           # Humidite relative a 2m (%)
      "QV2M",           # Humidite specifique (kg/kg)
      "WS2M",           # Vitesse du vent a 2m (m/s)
      "WS10M",          # Vitesse du vent a 10m (m/s)
      "WD2M",           # Direction du vent a 2m (degres)
      "PS",             # Pression de surface (kPa)
      "ALLSKY_SFC_SW_DWN",   # Rayonnement solaire global (MJ/m2/jour)
      "CLRSKY_SFC_SW_DWN",   # Rayonnement par ciel clair (MJ/m2/jour)
      "ALLSKY_SFC_SW_DIFF",  # Rayonnement diffus (MJ/m2/jour)
      "ALLSKY_SFC_LW_DWN",   # Rayonnement infrarouge (MJ/m2/jour)
      "T2MWET",              # Temperature thermometre mouille (degC)
      "WS50M",               # Vitesse du vent a 50m (m/s)
      "WD10M"                # Direction du vent a 10m (degres)
    )
  )
  return(weather_data)
}

# ==============================================================================
# ZONES AGRO-ECOLOGIQUES DU BENIN (8 points cles)
# ==============================================================================
zones <- data.frame(
  name = c("Cotonou", "Abomey-Calavi", "Save", "Parakou", "Natitingou", "Kandi", "Djougou", "Nikki"),
  lat = c(6.37, 7.15, 8.03, 9.35, 10.31, 11.13, 9.70, 9.94),
  lon = c(2.43, 2.05, 2.49, 2.63, 1.38, 2.94, 1.67, 3.21)
)

db_path <- "data/agridata.sqlite"
years <- 2020:2024

cat("Demarrage de la recuperation meteo pour 8 zones...\n")

all_weather_data <- data.frame()

# Boucle sur les zones
for (i in 1:nrow(zones)) {
  zone_name <- zones$name[i]
  zone_lat <- zones$lat[i]
  zone_lon <- zones$lon[i]
  
  cat(sprintf("\n--- Traitement de la zone : %s (Lat: %.2f, Lon: %.2f) ---\n", zone_name, zone_lat, zone_lon))
  
  # Boucle sur les annees pour eviter les timeouts
  for (year in years) {
    start_date <- paste0(year, "-01-01")
    end_date <- paste0(year, "-12-31")
    
    cat("  Annee", year, "...\n")
    
    tryCatch({
      yearly_data <- get_weather_data(zone_lon, zone_lat, start_date, end_date)
      
      # On ajoute nos coordonnees cibles car nasapower peut renvoyer la grille la plus proche
      yearly_data$target_lat <- zone_lat
      yearly_data$target_lon <- zone_lon
      
      all_weather_data <- rbind(all_weather_data, yearly_data)
      Sys.sleep(1) # Pause poli envers l'API
    }, error = function(e) {
      cat("  Erreur pour l'annee", year, ":", conditionMessage(e), "\n")
    })
  }
}

cat("\nToutes les donnees brutes recuperees. Formatage en cours...\n")

# Formatage
weather_data_formatted <- all_weather_data %>%
  mutate(
    latitude = target_lat,
    longitude = target_lon,
    date = as.character(YYYYMMDD)
  ) %>%
  select(
    latitude, longitude, date,
    precipitation_mm = PRECTOTCORR, temp_mean_c = T2M, temp_min_c = T2M_MIN, temp_max_c = T2M_MAX,
    temp_range_c = T2M_RANGE, temp_dew_c = T2MDEW, temp_surface_c = TS,
    humidity_pct = RH2M, humidity_specific = QV2M, wind_speed_2m = WS2M,
    wind_speed_10m = WS10M, wind_direction_2m = WD2M, pressure_kpa = PS,
    solar_radiation = ALLSKY_SFC_SW_DWN, solar_clear_sky = CLRSKY_SFC_SW_DWN,
    solar_diffuse = ALLSKY_SFC_SW_DIFF, longwave_radiation = ALLSKY_SFC_LW_DWN,
    temp_wet_bulb = T2MWET, wind_speed_50m = WS50M, wind_direction_10m = WD10M
  )

cat("Insertion dans la base de donnees...\n")
con <- dbConnect(RSQLite::SQLite(), db_path)

query <- "INSERT INTO weather_data (
            latitude, longitude, date, precipitation_mm, temp_mean_c, temp_min_c, 
            temp_max_c, temp_range_c, temp_dew_c, temp_surface_c, humidity_pct, 
            humidity_specific, wind_speed_2m, wind_speed_10m, wind_direction_2m, 
            pressure_kpa, solar_radiation, solar_clear_sky, solar_diffuse, 
            longwave_radiation, temp_wet_bulb, wind_speed_50m, wind_direction_10m
          ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
          ON CONFLICT(latitude, longitude, date) DO UPDATE SET 
            precipitation_mm = excluded.precipitation_mm,
            temp_mean_c = excluded.temp_mean_c,
            humidity_pct = excluded.humidity_pct;"

dbBegin(con)
for(i in 1:nrow(weather_data_formatted)) {
  row <- weather_data_formatted[i, ]
  params <- list(
    row$latitude, row$longitude, row$date, row$precipitation_mm, row$temp_mean_c, 
    row$temp_min_c, row$temp_max_c, row$temp_range_c, row$temp_dew_c, row$temp_surface_c, 
    row$humidity_pct, row$humidity_specific, row$wind_speed_2m, row$wind_speed_10m, 
    row$wind_direction_2m, row$pressure_kpa, row$solar_radiation, row$solar_clear_sky, 
    row$solar_diffuse, row$longwave_radiation, row$temp_wet_bulb, row$wind_speed_50m, 
    row$wind_direction_10m
  )
  dbExecute(con, query, params = params)
}
dbCommit(con)
dbDisconnect(con)

cat(sprintf("Termine ! %d lignes inserees pour les 8 zones.\n", nrow(weather_data_formatted)))