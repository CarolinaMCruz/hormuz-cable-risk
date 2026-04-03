# Hormuz Cable Risk
### Vulnerability Index for Coastal Cable Infrastructure in the Gulf Zone

---

## Overview

This project builds a **coastal infrastructure vulnerability index** for countries whose submarine cable landing points are located in the Gulf zone — the coastal entry and exit points where submarine cables are most exposed to damage.

Landing points represent the most vulnerable segment of any submarine cable system: they are accessible, concentrated, and surrounded by support infrastructure that can be disrupted by nearby conflict or instability.

---

## The Question This Project Answers

> *Which countries in the Gulf zone have the most exposed cable landing infrastructure, and how does nearby conflict increase their vulnerability?*

---

## Data Sources

| Source | Description | Access |
|--------|-------------|--------|
| [TeleGeography Submarine Cable Map](https://www.submarinecablemap.com) | Cable routes, landing points, owners, RFS dates | Public API |
| [UCDP Georeferenced Event Dataset](https://ucdp.uu.se/downloads) | Armed conflict events with coordinates, 1989–2026 | Free download |
| [UCDP Candidate Dataset](https://ucdp.uu.se/downloads) | Preliminary conflict events, monthly release | Free download |

---

## Methodology

The **Digital Vulnerability Index** is calculated per country using four components:

| Component | Weight | Description |
|-----------|--------|-------------|
| Exposure | 35% | UCDP conflict events within 50km of cable landing points (2020–2026) |
| Dependency | 30% | Share of a country's cables that pass through the Gulf risk zone |
| Redundancy | 20% | Total number of cables serving the country (inverse) |
| Concentration | 15% | Maximum number of cables sharing a single landing point |

Each component is normalized to [0, 1] before weighting.

---

## Results

| Country | Total Cables | Cables in Zone | Conflict Events | Risk Index |
|---------|-------------|----------------|-----------------|------------|
| Yemen | 5 | 5 | 569 | **0.652** |
| Pakistan | 9 | 9 | 306 | **0.487** |
| Iraq | 4 | 4 | 0 | 0.396 |
| Kuwait | 6 | 6 | 6 | 0.342 |
| Saudi Arabia | 24 | 24 | 0 | 0.312 |
| UAE | 21 | 21 | 8 | 0.283 |
| Iran | 6 | 6 | 13 | 0.278 |
| Qatar | 9 | 9 | 8 | 0.262 |
| Bahrain | 7 | 7 | 0 | 0.261 |
| Oman | 20 | 20 | 0 | **0.226** |

**Key finding:** Yemen and Pakistan show the highest vulnerability due to low cable redundancy combined with significant conflict activity near their coastal infrastructure. Oman, despite being geographically closest to the Strait, scores lowest due to high cable redundancy and absence of nearby conflict.

**Note on Iran:** The index likely underestimates Iran's actual risk. UCDP captures verified armed conflict events, not naval operations, sanctions-related disruptions, or geopolitical pressure — all of which significantly affect Iran's connectivity in practice.

---

## Outputs

- **`outputs/mapa_completo.html`** — Interactive map combining cable routes, conflict heatmap, landing points, and risk index by country
- **`outputs/mapa_riesgo.html`** — Simplified interactive risk map
- **`data/processed/indice_riesgo.csv`** — Full index table with all components

---

## Project Structure

```
hormuz-cable-risk/
├── README.md
├── requirements.txt
├── .gitignore
├── data/
│   ├── raw/               # Raw data files (not tracked in Git)
│   └── processed/         # Cleaned and processed datasets
│       ├── cables.csv
│       ├── landing_points.csv
│       ├── landing_points_coords.csv
│       ├── ucdp_gulf_zone.csv
│       └── indice_riesgo.csv
├── src/
│   ├── construir_dataset.py       # TeleGeography data pipeline
│   ├── combinar_ucdp.py           # Combines 4 UCDP CSV files
│   ├── explorar_telegeography.py  # TeleGeography exploration
│   ├── explorar_ucdp.py           # UCDP exploration
│   ├── indice_riesgo.py           # Risk index calculation
│   ├── mapa_riesgo.py             # Simple risk map
│   └── mapa_completo.py           # Combined interactive map
└── outputs/                       # Generated maps (not tracked in Git)
```

---

## How to Reproduce

```bash
# 1. Clone the repository
git clone https://github.com/CarolinaMCruz/hormuz-cable-risk.git
cd hormuz-cable-risk

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Download UCDP datasets manually
# Go to: https://ucdp.uu.se/downloads
# Download: GED Global v25.1, Candidate v25.01.25.12, v26.0.1, v26.0.2
# Place all CSV files in: data/raw/

# 5. Run the pipeline
python src/construir_dataset.py     # Build TeleGeography dataset
python src/combinar_ucdp.py         # Combine UCDP datasets
python src/indice_riesgo.py         # Calculate risk index
python src/mapa_completo.py         # Generate interactive map

# 6. Open the map
open outputs/mapa_completo.html
```

---

## Limitations

- UCDP data covers verified armed conflict events. Naval operations, cyber attacks, and geopolitical tensions are not captured, which likely underestimates risk for Iran and the broader US-Israel-Iran conflict context.
- Global Fishing Watch vessel presence data (AIS) was not integrated due to access restrictions. Adding vessel density near cable routes would significantly improve the exposure component.
- Cable route geometries from TeleGeography are cartographic representations, not precise engineering data.
- The index uses equal geographic treatment for all conflict events within the radius, regardless of whether they specifically target maritime infrastructure.
- AISstream real-time vessel tracking was tested but the service was unavailable at the time of development. The capture script (`src/capturar_ais.py`) is included for future use when the service is restored.
- This index measures risk at cable landing points (coastal infrastructure), not along submarine cable routes on the seafloor. Seabed risk from vessel anchoring or fishing requires AIS vessel traffic data, which was not available for this project.

---

## Tech Stack

- Python 3.12
- pandas, geopandas, shapely
- folium
- requests

---

*Data coverage: 1989 – February 2026*
