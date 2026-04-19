# Utiliser l'image de base officielle Python 3.11
FROM python:3.11-slim

# Metadonnees
LABEL maintainer="Agri-Assistant Team"
LABEL description="Backend FastAPI et scripts d'Agri-Assistant"

# Definir le repertoire de travail
WORKDIR /app

# Installer R et les dependances systeme requises
RUN apt-get update && apt-get install -y \
    r-base \
    r-base-dev \
    libcurl4-openssl-dev \
    libssl-dev \
    libxml2-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Installer les packages R requis (nasapower, dplyr, etc.)
RUN R -e "install.packages(c('nasapower', 'dplyr', 'lubridate'), repos='https://cloud.r-project.org/')"

# Copier les fichiers de dependances Python
COPY requirements.txt .

# Installer les dependances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier tout le code de l'application
COPY . .

# Exposer le port utilise par FastAPI
EXPOSE 8000

# Commande pour demarrer l'application avec Uvicorn
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
