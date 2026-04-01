"""
explorar_telegeography.py
Exploración inicial de los datos de TeleGeography.
Descarga los tres endpoints y genera un resumen de lo que contienen.

Requisitos:
    pip install requests pandas
"""

import requests
import pandas as pd

# ─────────────────────────────────────────────
# DESCARGA DE DATOS
# ─────────────────────────────────────────────

ENDPOINTS = {
    "cables_geo":    "https://www.submarinecablemap.com/api/v3/cable/cable-geo.json",
    "cables_lista":  "https://www.submarinecablemap.com/api/v3/cable/all.json",
    "landing_points": "https://www.submarinecablemap.com/api/v3/landing-point/landing-point-geo.json",
}


def descargar(nombre, url):
    print(f"  Descargando {nombre}...")
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    return r.json()


print("\n" + "="*55)
print("  EXPLORACIÓN - TeleGeography Submarine Cable Map")
print("="*55)

print("\n[1] Descargando datos...")
cables_geo = descargar("cables_geo", ENDPOINTS["cables_geo"])
cables_lista = descargar("cables_lista", ENDPOINTS["cables_lista"])
landing_geo = descargar("landing_points", ENDPOINTS["landing_points"])


# ─────────────────────────────────────────────
# EXPLORACIÓN: CABLES (lista maestra)
# ─────────────────────────────────────────────
print("\n[2] Explorando lista de cables...")

df_cables = pd.DataFrame(cables_lista)
print(f"\n  Columnas disponibles: {list(df_cables.columns)}")
print(f"  Total de cables: {len(df_cables)}")

# Cables por estado (activo, planificado, etc.)
if "status" in df_cables.columns:
    print("\n  Cables por estado:")
    print(df_cables["status"].value_counts().to_string())

# Muestra de cables con fecha de servicio
if "rfs" in df_cables.columns:
    activos = df_cables[df_cables["rfs"].notna()].sort_values(
        "rfs", ascending=False)
    print(f"\n  Cables con fecha RFS (Ready for Service): {len(activos)}")
    print(f"  Más recientes:")
    print(activos[["name", "rfs", "length"]].head(5).to_string(index=False))


# ─────────────────────────────────────────────
# EXPLORACIÓN: LANDING POINTS
# ─────────────────────────────────────────────
print("\n[3] Explorando puntos de aterrizaje...")

# Extraer propiedades del GeoJSON
landing_records = []
for feature in landing_geo["features"]:
    props = feature.get("properties", {})
    coords = feature.get("geometry", {}).get("coordinates", [None, None])
    landing_records.append({
        "id":      props.get("id"),
        "name":    props.get("name"),
        "country": props.get("country"),
        "lon":     coords[0],
        "lat":     coords[1],
    })

df_landing = pd.DataFrame(landing_records)
print(f"  Total puntos de aterrizaje: {len(df_landing)}")

print("\n  Top 15 países con más puntos de aterrizaje:")
print(df_landing["country"].value_counts().head(15).to_string())

# Países de la zona de interés
zona = ["Iran", "Oman", "United Arab Emirates", "Yemen", "Saudi Arabia",
        "Qatar", "Kuwait", "Bahrain", "Pakistan", "India"]

print("\n  Puntos de aterrizaje en zona de interés (Golfo/Ormuz):")
zona_df = df_landing[df_landing["country"].isin(zona)]
if len(zona_df) > 0:
    print(zona_df[["name", "country", "lat", "lon"]].to_string(index=False))
else:
    print("  Ninguno encontrado con esos nombres de país.")
    print("  Países únicos en el dataset (muestra):")
    print(df_landing["country"].dropna().unique()[:30])


# ─────────────────────────────────────────────
# EXPLORACIÓN: CABLES GEO (rutas)
# ─────────────────────────────────────────────
print("\n[4] Explorando rutas de cables (GeoJSON)...")

cable_records = []
for feature in cables_geo["features"]:
    props = feature.get("properties", {})
    cable_records.append({
        "id":     props.get("id"),
        "name":   props.get("name"),
        "color":  props.get("color"),
        "owners": props.get("owners", []),
    })

df_cables_geo = pd.DataFrame(cable_records)
print(f"  Total cables con geometría: {len(df_cables_geo)}")
print(f"  Columnas: {list(df_cables_geo.columns)}")
print(f"\n  Muestra de cables:")
print(df_cables_geo[["name"]].head(10).to_string(index=False))

print("\n" + "="*55)
print("  Exploración completada")
print("="*55 + "\n")
