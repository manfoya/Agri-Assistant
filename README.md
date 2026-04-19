# 🌿 Agri-Assistant

Agri-Assistant est un système intelligent de **recommandation de cultures** et d'évaluation agronomique, conçu pour les agriculteurs du Bénin. 

Il utilise une approche d'**Évaluation Multicritères (MCE)** instantanée : au lieu de se fier uniquement à des données historiques biaisées, le système croise les **coordonnées GPS exactes** (climatologie NASA POWER et composition du sol via SoilGrids) avec les exigences biologiques parfaites de 10 cultures cibles pour recommander celle qui produira le rendement maximal *à l'instant T*.

## ✨ Fonctionnalités Principales

- **Recommandation Instantanée par GPS** : L'algorithme calcule le score de compatibilité (0-100%) d'une culture en se basant uniquement sur la météo du mois en cours et la texture du sol.
- **Backend Rapide et Robuste** : Développé en Python avec **FastAPI**, incluant une base de données SQLite embarquée (`crop_requirements` et historique météo).
- **Frontend PWA Premium** : Une application mobile-first servie directement par le backend (HTML/CSS/JS Vanilla), offrant une expérience utilisateur fluide avec géolocalisation automatique.
- **Logs Anonymes** : Un système de suivi des recherches (`recommendation_log`) pour analyser l'utilisation sans collecter de données privées.
- **Scripts R de Data Science** : Le projet inclut des scripts R dédiés (`nasapower`) pour les calculs climatiques complexes (fenêtres de semis).

## 🛠️ Stack Technique

- **Backend** : Python 3.11, FastAPI, SQLAlchemy, Pydantic, Scikit-learn.
- **Frontend** : Vanilla HTML5, CSS3, JavaScript ES6 (Progressive Web App).
- **Data Science** : R, package `nasapower`.
- **Base de données** : SQLite.

## 🚀 Installation Locale (Développement)

1. **Cloner le dépôt**
   ```bash
   git clone https://github.com/manfoya/Agri-Assistant.git
   cd Agri-Assistant
   ```

2. **Créer et activer l'environnement virtuel Python**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

4. **Lancer le serveur FastAPI**
   ```bash
   uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload
   ```

5. **Accéder à l'application**
   - Interface PWA : `http://127.0.0.1:8000/`
   - Documentation API (Swagger) : `http://127.0.0.1:8000/docs`

## 🐳 Déploiement via Docker (Production)

L'application est prête à être déployée dans un environnement conteneurisé incluant Python et R.

```bash
# Construire l'image Docker
docker build -t agri-assistant .

# Lancer le conteneur sur le port 8000
docker run -d -p 8000:8000 agri-assistant
```

## 📂 Structure du Projet

```text
Agri-Assistant/
├── api/                    # Code source du backend FastAPI
│   ├── core/               # Configuration et DB
│   ├── models/             # Modèles SQLAlchemy (Soil, Weather, Crops, Logs)
│   ├── routers/            # Endpoints de l'API REST
│   ├── schemas/            # Validation de données Pydantic
│   └── services/           # Logique métier (Matching, NASA, SoilGrids)
├── data/                   # Base SQLite générée localement
├── ml/                     # Scripts ML et extraction de poids (Random Forest)
├── r_modules/              # Scripts R pour l'historique météo (nasapower)
├── static/                 # Frontend PWA (HTML, CSS, JS, Manifest, SW)
├── tests/                  # Tests unitaires de l'algorithme MCE
├── Dockerfile              # Configuration Docker de production
└── requirements.txt        # Dépendances Python
```

---
*Projet développé dans une optique de résilience climatique et d'amélioration des rendements agricoles.*
