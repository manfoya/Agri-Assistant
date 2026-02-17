# Agri-Assistant 

**Agri-Assistant** is an intelligent system designed to provide crop recommendations and sowing window predictions based on local soil and weather data in Benin.

## Architecture

The project follows a **Hybrid Data Science Architecture**:
*   **Python (FastAPI)**: Handles the API, data fetching, and system orchestration.
*   **R**: Handles advanced statistical modeling (Time Series) and data analysis.

👉 **[Read the detailed Architecture & Roles document](docs/architecture.md)**

## Project Structure

```
Agri-Assistant/
├── api/                # FastAPI Application (The "Backbone")
├── data/               # Local databases & datasets
├── docs/               # Documentation
├── notebooks/          # Jupyter/R Notebooks for Research
├── r_modules/          # R Scripts (The "Brain")
└── docker-compose.yml  # Deployment config
```

## Getting Started

### Prerequisites
*   Docker & Docker Compose
*   *Or* Python 3.10+ & R 4.x

### Quick Start (Docker)
The easiest way to run the full stack:

```bash
docker-compose up --build
```

The API will be available at: `http://localhost:8000`

### Manual Setup
1.  **Python Environment**:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```
2.  **R Environment**:
    Open `r_modules/` and let `renv` bootstrap itself, or run:
    ```bash
    Rscript -e "renv::restore()"
    ```
3.  **Run API**:
    ```bash
    uvicorn api.main:app --reload
    ```
