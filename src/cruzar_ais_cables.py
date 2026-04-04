"""
cruzar_ais_cables.py
Cruza datos de presencia AIS con rutas de cables submarinos.

Lógica:
  - Cada fila AIS representa una celda de 0.1° (~11km) con horas de tráfico
  - Para cada celda, calcula la distancia mínima al cable más cercano
  - Si la distancia es menor a 6km (mitad de la celda), asigna el tráfico al cable
  - El resultado es un índice de exposición por cable: horas de tráfico acumuladas

Output:
  data/processed/cables_exposicion_periodo1.csv
  data/processed/cables_exposicion_periodo2.csv
"""

import pandas as pd
import geopandas as gpd
import requests
from shapely.geometry import Point, MultiLineString, LineString
import os

os.makedirs("data/processed", exist_ok=True)

RADIO_M = 6000  # 6km = mitad de una celda LOW (0.1°)

# ── 1. Descargar rutas de cables (GeoJSON) ──────────────
print("\n[1] Descargando rutas de cables...")
r = requests.get(
    "https://www.submarinecablemap.com/api/v3/cable/cable-geo.json",
    timeout=20
)
cables_geo = r.json()
print(f"    Cables con geometría: {len(cables_geo['features'])}")

# Construir GeoDataFrame de cables
cable_records = []
for feature in cables_geo["features"]:
    props = feature["properties"]
    geom = feature["geometry"]
    if geom["type"] == "MultiLineString":
        lineas = [LineString(seg) for seg in geom["coordinates"] if len(seg) >= 2]
        if lineas:
            cable_records.append({
                "cable_id":   props["id"],
                "cable_name": props["name"],
                "geometry":   MultiLineString(lineas),
            })

gdf_cables = gpd.GeoDataFrame(cable_records, crs="EPSG:4326").to_crs("EPSG:3857")
print(f"    Cables procesados: {len(gdf_cables)}")

# ── 2. Función de cruce ─────────────────────────────────
def cruzar_con_cables(archivo_ais, nombre_periodo):
    print(f"\n[2] Procesando {nombre_periodo}...")
    df_ais = pd.read_csv(archivo_ais)
    df_ais = df_ais.dropna(subset=["lat", "lon", "hours"])
    print(f"    Registros AIS: {len(df_ais):,}")

    # Convertir celdas AIS a puntos geoespaciales
    df_ais["geometry"] = df_ais.apply(
        lambda r: Point(r["lon"], r["lat"]), axis=1
    )
    gdf_ais = gpd.GeoDataFrame(df_ais, crs="EPSG:4326").to_crs("EPSG:3857")

    # Para cada cable calcular horas de tráfico acumuladas
    print(f"    Cruzando {len(gdf_ais):,} celdas con {len(gdf_cables)} cables...")
    resultados = []

    for _, cable in gdf_cables.iterrows():
        # Buffer alrededor del cable
        cable_buffer = cable["geometry"].buffer(RADIO_M)

        # Celdas AIS dentro del buffer
        celdas_cerca = gdf_ais[gdf_ais["geometry"].within(cable_buffer)]

        if len(celdas_cerca) > 0:
            resultados.append({
                "cable_id":        cable["cable_id"],
                "cable_name":      cable["cable_name"],
                "horas_trafico":   celdas_cerca["hours"].sum(),
                "n_celdas":        len(celdas_cerca),
                "vessel_ids":      celdas_cerca["vessel_ids"].sum(),
                "n_banderas":      celdas_cerca["flag"].nunique(),
            })

    df_result = pd.DataFrame(resultados).sort_values("horas_trafico", ascending=False)
    return df_result


# ── 3. Procesar ambos períodos ──────────────────────────
df_p1 = cruzar_con_cables("data/processed/ais_periodo1.csv", "Período 1 (dic2025-ene2026)")
df_p2 = cruzar_con_cables("data/processed/ais_periodo2.csv", "Período 2 (feb2026-mar2026)")

# ── 4. Guardar resultados ───────────────────────────────
df_p1.to_csv("data/processed/cables_exposicion_periodo1.csv", index=False)
df_p2.to_csv("data/processed/cables_exposicion_periodo2.csv", index=False)

# ── 5. Resumen comparativo ──────────────────────────────
print("\n" + "="*55)
print("  TOP 10 CABLES - EXPOSICIÓN A TRÁFICO MARÍTIMO")
print("="*55)

print("\nPeríodo 1 (Pre-conflicto: dic2025-ene2026):")
print(df_p1[["cable_name","horas_trafico","vessel_ids","n_banderas"]].head(10).to_string(index=False))

print("\nPeríodo 2 (Conflicto activo: feb2026-mar2026):")
print(df_p2[["cable_name","horas_trafico","vessel_ids","n_banderas"]].head(10).to_string(index=False))

# Comparación de cambio
print("\n  CAMBIO EN EXPOSICIÓN (Período 1 vs Período 2):")
merged = df_p1[["cable_id","cable_name","horas_trafico"]].merge(
    df_p2[["cable_id","horas_trafico"]], on="cable_id", suffixes=("_p1","_p2")
)
merged["cambio_pct"] = ((merged["horas_trafico_p2"] - merged["horas_trafico_p1"]) /
                         merged["horas_trafico_p1"] * 100).round(1)
merged = merged.sort_values("cambio_pct")

print("\n  Cables con mayor reducción de tráfico:")
print(merged[["cable_name","horas_trafico_p1","horas_trafico_p2","cambio_pct"]].head(10).to_string(index=False))

print("\n" + "="*55)
print("  Archivos guardados en data/processed/")
print("="*55 + "\n")
