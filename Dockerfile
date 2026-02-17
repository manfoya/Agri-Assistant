# Utiliser une image Python légère
FROM python:3.10-slim

# Installer R et les dépendances système nécessaires
RUN apt-get update && apt-get install -y --no-install-recommends \
    r-base \
    build-essential \
    libsqlite3-dev \
    && rm -rf /var/lib/apt/lists/*

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de dépendances Python
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Installer les packages R via renv (si renv.lock existe)
# Pour l'instant, on installe juste les bases si nécessaire
# COPY r_modules/renv.lock r_modules/
# RUN Rscript -e "install.packages('renv'); renv::restore(project='r_modules')"

# Copier tout le code du projet
COPY . .

# Exposer le port pour l'API
EXPOSE 8000

# Commande de lancement
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
