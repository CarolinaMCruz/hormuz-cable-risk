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
| [Global Fishing Watch](https://globalfishingwatch.org/data/open-data/) | Vessel presence by cell (dataset: `public-global-presence:v4.0`) | `gfwapiclient` |

---

## Methodology

### Digital Vulnerability Index

The **Digital Vulnerability Index** is calculated per country using four components:

| Component | Weight | Description |
|-----------|--------|-------------|
| Exposure | 35% | UCDP conflict events within 50km of cable landing points (2020–2026) |
| Dependency | 30% | Share of a country's cables that pass through the Gulf risk zone |
| Redundancy | 20% | Total number of cables serving the country (inverse) |
| Concentration | 15% | Maximum number of cables sharing a single landing point |

Each component is normalized to [0, 1] before weighting.

### AIS Maritime Traffic Exposure

Vessel traffic density along submarine cable routes was estimated using Global Fishing Watch's vessel presence dataset (`public-global-presence:v4.0`). The methodology proceeds as follows:

1. **Grid construction:** The Gulf zone was divided into 0.1° × 0.1° cells (approximately 11 km × 11 km at regional latitudes).
2. **Cable assignment:** Each grid cell with registered vessel presence was assigned to the nearest submarine cable whose route geometry intersects or passes within a threshold distance of 6 km from the cell centroid. Cells beyond this threshold were excluded from cable-level aggregation.
3. **Traffic aggregation:** Total vessel-hours per cell were summed by cable to produce a per-cable exposure score representing the volume of surface traffic overlying each route segment.
4. **Temporal comparison:** Exposure was computed across two discrete periods to assess conflict-driven changes in maritime traffic patterns:
   - **Pre-conflict baseline** (January–September 2023)
   - **Active conflict period** (October 2023–March 2024)

#### Comparative Traffic Exposure by Cable

| Cable | Pre-Conflict (vessel-hours) | Active Conflict (vessel-hours) | Change |
|-------|----------------------------|-------------------------------|--------|
| FALCON | 184,210 | 121,580 | −34.0% |
| SEA-ME-WE 5 | 97,340 | 65,890 | −32.3% |
| AAE-1 | 88,760 | 60,410 | −31.9% |
| IMEWE | 72,530 | 51,200 | −29.4% |
| EIG | 61,880 | 44,320 | −28.4% |

**Aggregate finding:** Total vessel traffic over monitored cable corridors declined by **34%** between the pre-conflict baseline and the active conflict period, consistent with documented shipping route diversions following the escalation of Houthi attacks on commercial vessels in the southern Red Sea and Gulf of Aden.

**FALCON cable finding:** FALCON ranks as the most exposed cable in both periods. It is also the only cable connecting Iran to the global internet outside the Persian Gulf basin. A disruption to the FALCON cable would effectively isolate Iran from **184 out of 185** countries reachable via submarine infrastructure, representing a near-total severance of its international connectivity.

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

**Note on Iran:** The index likely underestimates Iran's actual risk. UCDP captures verified armed conflict events, not naval operations, sanctions-related disruptions, or geopolitical pressure — all of which significantly affect Iran's connectivity in practice. The FALCON cable finding further compounds this assessment.

---

## Outputs

- **`outputs/mapa_completo.html`** — Interactive map combining cable routes, conflict heatmap, landing points, and risk index by country
- **`outputs/mapa_riesgo.html`** — Simplified interactive risk map
- **`data/processed/indice_riesgo.csv`** — Full index table with all components
- **`data/processed/ais_exposure_by_cable.csv`** — Vessel traffic exposure per cable, pre- and post-conflict periods
- **`data/processed/ais_grid_cells.csv`** — Raw 0.1° grid cells with vessel-hours and cable assignment

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
│       ├── indice_riesgo.csv
│       ├── ais_exposure_by_cable.csv
│       └── ais_grid_cells.csv
├── src/
│   ├── construir_dataset.py       # TeleGeography data pipeline
│   ├── combinar_ucdp.py           # Combines 4 UCDP CSV files
│   ├── explorar_telegeography.py  # TeleGeography exploration
│   ├── explorar_ucdp.py           # UCDP exploration
│   ├── indice_riesgo.py           # Risk index calculation
│   ├── ais_exposure.py            # GFW vessel presence pipeline and cable assignment
│   ├── ais_comparar_periodos.py   # Pre/post-conflict traffic comparison
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

# 5. Set GFW API credentials
export GFW_API_TOKEN=your_token_here

# 6. Run the pipeline
python src/construir_dataset.py     # Build TeleGeography dataset
python src/combinar_ucdp.py         # Combine UCDP datasets
python src/ais_exposure.py          # Fetch GFW vessel presence and assign to cables
python src/ais_comparar_periodos.py # Compute pre/post-conflict traffic comparison
python src/indice_riesgo.py         # Calculate risk index
python src/mapa_completo.py         # Generate interactive map

# 7. Open the map
open outputs/mapa_completo.html
```

---

## Limitations

- UCDP data covers verified armed conflict events. Naval operations, cyber attacks, and geopolitical tensions are not captured, which likely underestimates risk for Iran and the broader US-Israel-Iran conflict context.
- Cable route geometries from TeleGeography are cartographic representations, not precise engineering data.
- The index uses equal geographic treatment for all conflict events within the radius, regardless of whether they specifically target maritime infrastructure.
- The AIS exposure component is derived from Global Fishing Watch vessel presence data (`public-global-presence:v4.0`), which aggregates all vessel classes. It does not distinguish between fishing vessels, commercial shipping, and naval assets, which limits precision in attributing traffic to specific risk categories.
- This index measures risk at cable landing points (coastal infrastructure) and along cable route corridors, but does not model seabed-level risk from anchoring or trawling at depth. Full seabed risk assessment would require higher-resolution bathymetric and vessel track data.
- The 0.1° grid cell assignment uses minimum distance to cable route geometry as a proxy for exposure. Cells near route intersections or branching points may be assigned to a single cable when multiple cables are at similar distances, introducing minor aggregation uncertainty.

---

## Tech Stack

- Python 3.12
- pandas, geopandas, shapely
- folium
- networkx
- requests
- gfwapiclient

---

*Data coverage: 1989 – March 2026*
