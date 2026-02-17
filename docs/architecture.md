# Architecture & Technology Roles - Agri-Assistant

This document defines the strategic split between **Python** and **R** in the Agri-Assistant project. We leverage the specific strengths of each ecosystem to build a robust product.

## 1. Top-Level Overview

| Tech | Role | Metaphor | Key Libraries |
|------|------|----------|---------------|
| **Python** | **Application & Engineering** | The "Body" & "Nerves" | `FastAPI`, `Pydantic`, `SQLAlchemy`, `Docker` |
| **R** | **Statistical Intelligence & Data Fetching** | The "Brain" & "Sensors" | `nasapower`, `forecast`, `tseries`, `ggplot2`, `dplyr` |

## 2. Python Role: The Engineering Backbone
Python is used for everything related to **production**, **automation**, and **interfacing**.

*   **API (FastAPI)**: Exposes the intelligence to the outside world (Mobile App, Frontend).
*   **Orchestration**: Managing the database and triggering R scripts.
*   **Validation**: Ensuring input data is correct (Pydantic).
*   **Deployment**: straightforward containerization with Docker.
*   **Soil Data**: Python handles fetching soil data from ISRIC/SoilGrids APIs.

## 3. R Role: The Statistical Core & Specialized Data
R is used for its superior capabilities in **statistical modeling** and its **specialized scientific libraries**.

*   **Climate Data Retrieval (`nasapower`)**: R is responsible for fetching historical weather data from NASA POWER because it has the most robust and maintained library for this specific scientific source.
*   **Time Series Analysis (ARIMA/SARIMA)**: R's `forecast` and `stats` packages are the gold standard for statistical time series analysis.
*   **Exploratory Data Analysis (EDA)**: Using R Notebooks for deep statistical dives into climate data.

## 4. Interaction Workflow

How do they talk to each other?

1.  **Request**: User asks for a recommendation via API (Python).
2.  **Data Fetching**:
    *   Python fetches Soil Data.
    *   Python triggers **R Script** to fetch/update Weather Data (via `nasapower`).
3.  **Calculation**: Python triggers an **R Script** for the model.
    *   R loads the trained model.
    *   R computes the prediction (e.g., "Start sowing on May 15th").
    *   R returns the result (JSON).
4.  **Response**: Python parses the R result and sends it back to the user.

> **Why R for Data Fetching?**
> The `nasapower` R package is a specialized tool that simplifies complex API queries for agro-climatology. Recreating this logic in Python would be redundant and less reliable.
