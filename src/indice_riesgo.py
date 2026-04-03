"""
indice_riesgo.py
Calcula el índice de vulnerabilidad digital por país basado en:
  1. Dependencia   - % de cables que pasan por zona de riesgo
  2. Redundancia   - total de cables del país (inverso)
  3. Exposición    - eventos de conflicto UCDP cerca de sus landing points
  4. Concentración - landing points con muchos cables en zona de riesgo

Output: data/processed/indice_riesgo.csv
        outputs/indice_riesgo.html
"""

import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import Point
import folium
import os

os.makedirs("outputs", exist_ok=True)

ZONA = [
    "Iran", "Oman", "Yemen", "Yemen (North Yemen)", "Saudi Arabia",
    "United Arab Emirates", "Qatar", "Kuwait", "Bahrain",
    "Pakistan", "Iraq"
]

RADIO_KM = 50  # radio para considerar conflicto "cercano" a un landing point

print("\n" + "="*55)
print("  ÍNDICE DE RIESGO - Vulnerabilidad digital por país")
print("="*55)

# ── 1. Cargar datos ─────────────────────────────────────
print("\n[1] Cargando datos...")
df_landing = pd.read_csv("data/processed/landing_points.csv")
df_coords = pd.read_csv("data/processed/landing_points_coords.csv")
df_landing = df_landing.merge(df_coords, on="landing_id", how="left")
df_cables = pd.read_csv("data/processed/cables.csv")
df_conflicto = pd.read_csv(
    "data/processed/ucdp_gulf_zone.csv", low_memory=False)
df_conflicto = df_conflicto.dropna(subset=["latitude", "longitude"])
df_conflicto["country"] = df_conflicto["country"].replace(
    {"Yemen (North Yemen)": "Yemen"})
df_conflicto["date_start"] = pd.to_datetime(df_conflicto["date_start"])
df_conflicto = df_conflicto[df_conflicto["date_start"].dt.year >= 2020]

print(f"    Landing points: {len(df_landing)}")
print(f"    Cables: {len(df_cables)}")
print(f"    Eventos conflicto zona: {len(df_conflicto)}")

# ── 2. Componente 1: Dependencia ────────────────────────
print("\n[2] Calculando dependencia por país...")

# Cables totales por país
cables_totales = (
    df_landing.groupby("country")["cable_id"]
    .nunique()
    .reset_index(name="cables_totales")
)

# Cables en zona de riesgo por país
lp_zona = df_landing[df_landing["country"].isin(ZONA)]
cables_zona = (
    lp_zona.groupby("country")["cable_id"]
    .nunique()
    .reset_index(name="cables_zona")
)

df_pais = cables_totales.merge(cables_zona, on="country", how="left")
df_pais["cables_zona"] = df_pais["cables_zona"].fillna(0)
df_pais["dependencia"] = df_pais["cables_zona"] / df_pais["cables_totales"]

# Solo países de la zona
df_pais = df_pais[df_pais["country"].isin(ZONA)].copy()
print(f"    Países en zona: {len(df_pais)}")

# ── 3. Componente 2: Redundancia (inversa) ──────────────
print("\n[3] Calculando redundancia...")

# Más cables = más redundancia = menos riesgo
# Normalizamos inversamente: menos cables = score más alto
df_pais["redundancia_inv"] = 1 / df_pais["cables_totales"]

# ── 4. Componente 3: Exposición a conflicto ─────────────
print("\n[4] Calculando exposición a conflicto...")

# Convertir landing points a GeoDataFrame
lp_zona_geo = lp_zona.dropna(subset=["latitude", "longitude"]).copy()
lp_zona_geo["geometry"] = lp_zona_geo.apply(
    lambda r: Point(r["longitude"], r["latitude"]), axis=1
)
gdf_lp = gpd.GeoDataFrame(lp_zona_geo, crs="EPSG:4326")

# Convertir conflictos a GeoDataFrame
df_conflicto["geometry"] = df_conflicto.apply(
    lambda r: Point(r["longitude"], r["latitude"]), axis=1
)
gdf_conf = gpd.GeoDataFrame(df_conflicto, crs="EPSG:4326")

# Proyectar a metros para calcular distancias reales
gdf_lp_m = gdf_lp.to_crs("EPSG:3857")
gdf_conf_m = gdf_conf.to_crs("EPSG:3857")

# Para cada landing point, contar eventos dentro del radio
radio_m = RADIO_KM * 1000
exposicion_por_lp = []

for _, lp in gdf_lp_m.iterrows():
    buffer = lp["geometry"].buffer(radio_m)
    eventos_cercanos = gdf_conf_m[gdf_conf_m["geometry"].within(buffer)]
    exposicion_por_lp.append({
        "landing_id": lp["landing_id"],
        "country":    lp["country"],
        "n_eventos":  len(eventos_cercanos),
        "muertes":    eventos_cercanos["best"].sum(),
    })

df_exposicion = pd.DataFrame(exposicion_por_lp)
exposicion_pais = (
    df_exposicion.groupby("country")
    .agg(eventos_totales=("n_eventos", "sum"), muertes_totales=("muertes", "sum"))
    .reset_index()
)

df_pais = df_pais.merge(exposicion_pais, on="country", how="left")
df_pais["eventos_totales"] = df_pais["eventos_totales"].fillna(0)
df_pais["muertes_totales"] = df_pais["muertes_totales"].fillna(0)

# ── 5. Componente 4: Concentración ─────────────────────
print("\n[5] Calculando concentración de infraestructura...")

cables_por_lp = df_landing.groupby(
    "landing_id").size().reset_index(name="n_cables")
lp_zona_conc = lp_zona.merge(cables_por_lp, on="landing_id", how="left")

concentracion_pais = (
    lp_zona_conc.groupby("country")["n_cables"]
    .max()
    .reset_index(name="max_cables_por_lp")
)

df_pais = df_pais.merge(concentracion_pais, on="country", how="left")

# ── 6. Normalizar y calcular índice final ───────────────
print("\n[6] Calculando índice final...")


def normalizar(serie):
    mn, mx = serie.min(), serie.max()
    if mx == mn:
        return pd.Series([0.5] * len(serie), index=serie.index)
    return (serie - mn) / (mx - mn)


df_pais["n_dependencia"] = normalizar(df_pais["dependencia"])
df_pais["n_redundancia"] = normalizar(df_pais["redundancia_inv"])
df_pais["n_exposicion"] = normalizar(df_pais["eventos_totales"])
df_pais["n_concentracion"] = normalizar(df_pais["max_cables_por_lp"])

# Pesos del índice
PESOS = {
    "n_dependencia":   0.30,
    "n_redundancia":   0.20,
    "n_exposicion":    0.35,
    "n_concentracion": 0.15,
}

df_pais["indice_riesgo"] = sum(
    df_pais[col] * peso for col, peso in PESOS.items()
)

df_pais["indice_riesgo"] = df_pais["indice_riesgo"].round(3)
df_pais = df_pais.sort_values("indice_riesgo", ascending=False)

# ── 7. Mostrar resultados ───────────────────────────────
print("\n" + "="*55)
print("  RESULTADOS: Índice de Vulnerabilidad Digital")
print("="*55)
print(f"\n  Radio de exposición: {RADIO_KM} km\n")

cols_mostrar = [
    "country", "cables_totales", "cables_zona",
    "eventos_totales", "max_cables_por_lp", "indice_riesgo"
]
print(df_pais[cols_mostrar].to_string(index=False))

# ── 8. Guardar CSV ──────────────────────────────────────
df_pais.to_csv("data/processed/indice_riesgo.csv", index=False)
print(f"\n  Guardado: data/processed/indice_riesgo.csv")

# ── 9. Mapa de resultados ───────────────────────────────
print("\n[7] Generando mapa del índice...")

mapa = folium.Map(location=[24.0, 57.0],
                  zoom_start=4, tiles="CartoDB dark_matter")

# Color por índice de riesgo


def color_riesgo(indice):
    if indice >= 0.7:
        return "#ff2222"
    elif indice >= 0.5:
        return "#ff8800"
    elif indice >= 0.3:
        return "#ffdd00"
    else:
        return "#44bb44"


# Coordenadas aproximadas por país para el marcador
coords_pais = {
    "Iran":                  [32.0, 53.0],
    "Iraq":                  [33.0, 44.0],
    "Yemen (North Yemen)":   [15.5, 48.0],
    "Saudi Arabia":          [24.0, 45.0],
    "United Arab Emirates":  [24.5, 54.5],
    "Oman":                  [22.0, 57.5],
    "Qatar":                 [25.3, 51.2],
    "Kuwait":                [29.3, 47.7],
    "Bahrain":               [26.0, 50.5],
    "Pakistan":              [30.0, 69.0],
}

for _, row in df_pais.iterrows():
    coords = coords_pais.get(row["country"])
    if not coords:
        continue

    folium.CircleMarker(
        location=coords,
        radius=10 + (row["indice_riesgo"] * 20),
        color=color_riesgo(row["indice_riesgo"]),
        fill=True,
        fill_color=color_riesgo(row["indice_riesgo"]),
        fill_opacity=0.8,
        popup=folium.Popup(
            f"<b>{row['country']}</b><br>"
            f"Índice de riesgo: <b>{row['indice_riesgo']}</b><br>"
            f"Cables totales: {int(row['cables_totales'])}<br>"
            f"Cables en zona: {int(row['cables_zona'])}<br>"
            f"Eventos conflicto cercanos: {int(row['eventos_totales'])}<br>"
            f"Max cables por landing point: {int(row['max_cables_por_lp'])}",
            max_width=280
        ),
        tooltip=f"{row['country']}: {row['indice_riesgo']}",
    ).add_to(mapa)

# Leyenda
leyenda_html = """
<div style="position: fixed; bottom: 30px; left: 30px; z-index: 1000;
     background-color: rgba(0,0,0,0.75); padding: 15px; border-radius: 8px;
     color: white; font-family: Arial; font-size: 12px; min-width: 220px;">
  <b>Índice de Vulnerabilidad Digital</b><br>
  <i>Cables submarinos - Zona del Golfo</i><br><br>
  <b>Nivel de riesgo:</b><br>
  <span style="color:#ff2222;">&#9679;</span> Alto (&ge; 0.70)<br>
  <span style="color:#ff8800;">&#9679;</span> Medio-alto (0.50 - 0.69)<br>
  <span style="color:#ffdd00;">&#9679;</span> Medio (0.30 - 0.49)<br>
  <span style="color:#44bb44;">&#9679;</span> Bajo (&lt; 0.30)<br><br>
  <i>Tamaño del círculo proporcional al índice</i><br><br>
  <b>Componentes:</b><br>
  Dependencia (30%) + Exposición (35%)<br>
  + Redundancia (20%) + Concentración (15%)
</div>
"""
mapa.get_root().html.add_child(folium.Element(leyenda_html))
folium.LayerControl().add_to(mapa)

mapa.save("outputs/indice_riesgo.html")
print("  Guardado: outputs/indice_riesgo.html")
print("  Abre con: open outputs/indice_riesgo.html\n")
