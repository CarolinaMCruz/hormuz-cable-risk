"""
inspeccionar_estructura.py
Inspecciona la estructura real de los datos de TeleGeography
para entender qué campos están disponibles.
"""

import requests
import json

ENDPOINTS = {
    "cables_lista":  "https://www.submarinecablemap.com/api/v3/cable/all.json",
    "landing_points":"https://www.submarinecablemap.com/api/v3/landing-point/landing-point-geo.json",
    "cables_geo":    "https://www.submarinecablemap.com/api/v3/cable/cable-geo.json",
}

def descargar(url):
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    return r.json()

print("\n" + "="*55)
print("  INSPECCIÓN DE ESTRUCTURA - TeleGeography")
print("="*55)

# ── 1. Lista de cables ──────────────────────────────────
print("\n[1] Primer registro de cables_lista:")
cables_lista = descargar(ENDPOINTS["cables_lista"])
print(json.dumps(cables_lista[0], indent=2))

# ── 2. Landing points GeoJSON ───────────────────────────
print("\n[2] Primer feature de landing_points:")
landing = descargar(ENDPOINTS["landing_points"])
print(json.dumps(landing["features"][0], indent=2))

# ── 3. Cable geo ────────────────────────────────────────
print("\n[3] Primer feature de cables_geo (sin coordenadas para no saturar):")
cables_geo = descargar(ENDPOINTS["cables_geo"])
feature = cables_geo["features"][0].copy()
# Omitir coordenadas para que sea legible
if "geometry" in feature:
    feature["geometry"] = {"type": feature["geometry"]["type"], "coordinates": "(...omitido...)"}
print(json.dumps(feature, indent=2))

# ── 4. Endpoint de cable individual ─────────────────────
# Tomar el id del primer cable y buscar su detalle
primer_id = cables_lista[0]["id"]
print(f"\n[4] Detalle de cable individual (id: {primer_id}):")
url_cable = f"https://www.submarinecablemap.com/api/v3/cable/{primer_id}.json"
try:
    cable_detalle = descargar(url_cable)
    print(json.dumps(cable_detalle, indent=2))
except Exception as e:
    print(f"  No disponible: {e}")

# ── 5. Landing point individual ─────────────────────────
primer_lp_id = landing["features"][0]["properties"].get("id")
print(f"\n[5] Detalle de landing point individual (id: {primer_lp_id}):")
url_lp = f"https://www.submarinecablemap.com/api/v3/landing-point/{primer_lp_id}.json"
try:
    lp_detalle = descargar(url_lp)
    print(json.dumps(lp_detalle, indent=2))
except Exception as e:
    print(f"  No disponible: {e}")

print("\n" + "="*55)
print("  Inspección completada")
print("="*55 + "\n")
