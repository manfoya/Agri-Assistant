library("chirps")
get_weather_data <- function(lon, lat, start_date, end_date, server = "CHC") {
  # Ensure dates are in character format
  start_date <- as.character(as.Date(start_date))
  end_date <- as.character(as.Date(end_date))
  
  # Create object with coordinates
  lonlat <- data.frame(lon = lon, lat = lat)
  
  # Create dates vector
  dates <- c(start_date, end_date)
  
  # Fetch CHIRPS data
  weather_data <- chirps::get_chirps(
    object = lonlat,
    dates = dates,
    server = server
  )
  
  return(weather_data)
}

# Test function with error handling
test_weather_data <- function(lon, lat, start_date, end_date) {
  cat("Testing with CHC server...\n")
  tryCatch({
    result_chc <- get_weather_data(lon, lat, start_date, end_date, server = "CHC")
    return(result_chc)
  }, error = function(e) {
    cat("CHC server failed:", e$message, "\n")
    cat("Trying ClimateSERV server...\n")
    tryCatch({
      result_cs <- get_weather_data(lon, lat, start_date, end_date, server = "ClimateSERV")
      return(result_cs)
    }, error = function(e2) {
      cat("ClimateSERV server also failed:", e2$message, "\n")
      return(NULL)
    })
  })
}

# Example usage avec coordonnées valides (Bénin/Afrique de l'Ouest):
weather <- test_weather_data(2.05, 7.15, "2023-01-01", "2023-01-31")
print(weather)