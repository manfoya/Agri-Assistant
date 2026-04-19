# Calcul du debut de la saison des pluies (Onset) par zone
# Definition agronomique :
# - Au moins 20mm de pluie sur 3 jours consecutifs.
# - Pas de periode seche de plus de 7 jours dans les 30 jours suivants.

library(RSQLite)
library(dplyr)
library(zoo)

db_path <- "data/agridata.sqlite"
con <- dbConnect(RSQLite::SQLite(), db_path)

# Recuperer toutes les donnees meteo
weather_data <- dbGetQuery(con, "SELECT latitude, longitude, date, precipitation_mm FROM weather_data ORDER BY latitude, longitude, date")

# Fonction pour trouver l'onset pour une annee donnee
find_onset <- function(df, start_month = "03") {
  # Filtrer a partir du mois de recherche (Mars pour le Sud, Mai pour le Nord en general, 
  # on simplifie en cherchant a partir de Mars partout)
  df_year <- df %>% filter(format(as.Date(date), "%m") >= "03")
  
  if(nrow(df_year) < 30) return(NA)
  
  # Calculer la somme glissante sur 3 jours
  df_year$sum_3d <- rollapply(df_year$precipitation_mm, width = 3, FUN = sum, align = "right", fill = NA)
  
  # Parcourir chaque jour potentiel d'onset
  for (i in 3:(nrow(df_year) - 30)) {
    if (!is.na(df_year$sum_3d[i]) && df_year$sum_3d[i] >= 20) {
      # Onset potentiel trouve a df_year$date[i]. 
      # Verifier la condition de secheresse dans les 30 jours suivants
      # (Pas plus de 7 jours consecutifs avec < 1mm)
      
      next_30_days <- df_year$precipitation_mm[(i+1):(i+30)]
      is_dry <- next_30_days < 1.0
      
      # Chercher la plus longue sequence de jours secs
      max_dry_spell <- 0
      current_spell <- 0
      for (dry in is_dry) {
        if (dry) {
          current_spell <- current_spell + 1
          if (current_spell > max_dry_spell) max_dry_spell <- current_spell
        } else {
          current_spell <- 0
        }
      }
      
      # Si pas de fausse saison (secheresse <= 7j), c'est le bon onset !
      if (max_dry_spell <= 7) {
        return(df_year$date[i])
      }
    }
  }
  return(NA)
}

# Analyser par zone et par annee
cat("Calcul des dates d'onset historiques...\n")

results <- data.frame(latitude=numeric(), longitude=numeric(), year=numeric(), onset_date=character())

locations <- unique(weather_data[, c("latitude", "longitude")])

for (i in 1:nrow(locations)) {
  lat <- locations$latitude[i]
  lon <- locations$longitude[i]
  
  df_loc <- weather_data %>% filter(latitude == lat & longitude == lon)
  
  # Extraire les annees uniques
  df_loc$year <- format(as.Date(df_loc$date), "%Y")
  years <- unique(df_loc$year)
  
  for (y in years) {
    df_year <- df_loc %>% filter(year == y)
    onset <- find_onset(df_year)
    
    if (!is.na(onset)) {
      results <- rbind(results, data.frame(
        latitude = lat, longitude = lon, year = y, onset_date = onset
      ))
    }
  }
}

# Creer une table de synthese : date moyenne d'onset par zone
cat("Synthese des resultats...\n")

# Extraire le "jour de l'annee" (DOY) pour faire des moyennes
results$doy <- as.numeric(format(as.Date(results$onset_date), "%j"))

summary_onset <- results %>%
  group_by(latitude, longitude) %>%
  summarise(
    avg_doy = mean(doy, na.rm = TRUE),
    min_onset = min(onset_date),
    max_onset = max(onset_date),
    years_calculated = n(),
    .groups = 'drop'
  )

# Reconvertir le DOY moyen en date format Mois-Jour
summary_onset$avg_onset_date <- format(as.Date(paste0("2024-", summary_onset$avg_doy), format="%Y-%j"), "%m-%d")

print(summary_onset)

# Sauvegarder dans la base de donnees
dbExecute(con, "DROP TABLE IF EXISTS historical_onset;")
dbWriteTable(con, "historical_onset", summary_onset, row.names = FALSE)

dbDisconnect(con)
cat("Calcul termine. Table 'historical_onset' creee dans la base de donnees.\n")
