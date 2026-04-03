"""
mapa_completo.py
Mapa interactivo combinado con:
  - Rutas reales de cables submarinos (TeleGeography GeoJSON)
  - Landing points coloreados por país
  - Heatmap de conflicto UCDP (2020-2026)
  - Índice de riesgo por país

Output: outputs/mapa_completo.html
"""

import requests
import pandas as pd
import folium
from folium.plugins import HeatMap
import os

os.makedirs("outputs", exist_ok=True)

ZONA = [
    "Iran", "Oman", "Yemen", "Saudi Arabia",
    "United Arab Emirates", "Qatar", "Kuwait", "Bahrain",
    "Pakistan", "Iraq"
]

# ── 1. Cargar datos locales ─────────────────────────────
print("Cargando datos...")
df_landing = pd.read_csv("data/processed/landing_points.csv")
df_coords = pd.read_csv("data/processed/landing_points_coords.csv")
df_landing = df_landing.merge(df_coords, on="landing_id", how="left")
df_conflicto = pd.read_csv(
    "data/processed/ucdp_gulf_zone.csv", low_memory=False)
df_conflicto = df_conflicto.dropna(subset=["latitude", "longitude"])
df_conflicto["date_start"] = pd.to_datetime(df_conflicto["date_start"])
df_conflicto["country"] = df_conflicto["country"].replace(
    {"Yemen (North Yemen)": "Yemen"})
df_indice = pd.read_csv("data/processed/indice_riesgo.csv")

# ── 2. Descargar GeoJSON de cables ──────────────────────
print("Descargando rutas de cables...")
r = requests.get(
    "https://www.submarinecablemap.com/api/v3/cable/cable-geo.json",
    timeout=20
)
cables_geo = r.json()

r2 = requests.get(
    "https://www.submarinecablemap.com/api/v3/cable/all.json",
    timeout=20
)
cables_lista = {c["id"]: c["name"] for c in r2.json()}
print(f"    Cables con geometría: {len(cables_geo['features'])}")

# ── 3. Crear mapa base ──────────────────────────────────
print("Generando mapa...")
mapa = folium.Map(
    location=[24.0, 57.0],
    zoom_start=4,
    tiles="CartoDB dark_matter"
)

# ── 4. Rutas de cables (capa desactivada por defecto) ───
fg_cables = folium.FeatureGroup(name="Rutas de cables submarinos", show=True)

# Cables que tocan la zona del Golfo
lp_zona = df_landing[df_landing["country"].isin(ZONA)]
cables_zona_ids = set(lp_zona["cable_id"].unique())

for feature in cables_geo["features"]:
    cable_id = feature["properties"]["id"]
    cable_name = feature["properties"]["name"]
    color = feature["properties"].get("color", "#888888")
    es_zona = cable_id in cables_zona_ids

    # Cables en zona: más visibles; resto: más tenues
    opacidad = 0.9 if es_zona else 0.15
    peso = 2 if es_zona else 1

    geom = feature["geometry"]
    if geom["type"] == "MultiLineString":
        for linea in geom["coordinates"]:
            puntos = [[p[1], p[0]] for p in linea]
            if len(puntos) < 2:
                continue
            folium.PolyLine(
                locations=puntos,
                color=color,
                weight=peso,
                opacity=opacidad,
                tooltip=cable_name if es_zona else None,
            ).add_to(fg_cables)

fg_cables.add_to(mapa)

# ── 5. Heatmap de conflictos (2020-2026) ────────────────
conflicto_reciente = df_conflicto[df_conflicto["date_start"].dt.year >= 2020]
heat_data = conflicto_reciente[[
    "latitude", "longitude", "best"]].values.tolist()

HeatMap(
    heat_data,
    name="Intensidad de conflicto (2020-2026)",
    min_opacity=0.3,
    radius=18,
    blur=15,
    gradient={0.2: "blue", 0.5: "yellow", 0.8: "orange", 1.0: "red"},
).add_to(mapa)

# ── 6. Landing points en zona del Golfo ─────────────────
colores_pais = {
    "Iran":                  "#ff4444",
    "Iraq":                  "#ff8800",
    "Yemen":                 "#cc0000",
    "Saudi Arabia":          "#44bb44",
    "United Arab Emirates":  "#4488ff",
    "Oman":                  "#88ddff",
    "Qatar":                 "#bb44bb",
    "Kuwait":                "#ffaacc",
    "Bahrain":               "#44ccbb",
    "Pakistan":              "#006600",
}

fg_landing = folium.FeatureGroup(name="Landing Points")
cables_por_lp = df_landing.groupby(
    "landing_id").size().reset_index(name="n_cables")
lp_zona = lp_zona.merge(cables_por_lp, on="landing_id", how="left")

for _, row in lp_zona.iterrows():
    if pd.isna(row["latitude"]) or pd.isna(row["longitude"]):
        continue
    color = colores_pais.get(row["country"], "#aaaaaa")
    n = row.get("n_cables", 1)

    folium.CircleMarker(
        location=[row["latitude"], row["longitude"]],
        radius=4 + (n * 1.5),
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.9,
        popup=folium.Popup(
            f"<b>{row['landing_name']}</b><br>"
            f"País: {row['country']}<br>"
            f"Cables: {int(n)}",
            max_width=220
        ),
        tooltip=f"{row['landing_name']} ({int(n)} cables)",
    ).add_to(fg_landing)

fg_landing.add_to(mapa)

# ── 7. Índice de riesgo por país ─────────────────────────


def color_riesgo(indice):
    if indice >= 0.6:
        return "#ff2222"
    elif indice >= 0.45:
        return "#ff8800"
    elif indice >= 0.30:
        return "#ffdd00"
    else:
        return "#44bb44"


coords_pais = {
    "Iran":                  [32.0, 53.0],
    "Iraq":                  [33.0, 44.0],
    "Yemen":                 [15.5, 48.0],
    "Saudi Arabia":          [24.0, 45.0],
    "United Arab Emirates":  [24.5, 54.5],
    "Oman":                  [22.0, 57.5],
    "Qatar":                 [25.3, 51.2],
    "Kuwait":                [29.3, 47.7],
    "Bahrain":               [26.0, 50.5],
    "Pakistan":              [30.0, 69.0],
}

fg_indice = folium.FeatureGroup(name="Índice de riesgo por país")

for _, row in df_indice.iterrows():
    coords = coords_pais.get(row["country"])
    if not coords:
        continue
    color = color_riesgo(row["indice_riesgo"])

    folium.CircleMarker(
        location=coords,
        radius=12 + (row["indice_riesgo"] * 18),
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.6,
        popup=folium.Popup(
            f"<b>{row['country']}</b><br>"
            f"Índice: <b>{row['indice_riesgo']}</b><br>"
            f"Cables totales: {int(row['cables_totales'])}<br>"
            f"Cables en zona: {int(row['cables_zona'])}<br>"
            f"Eventos conflicto: {int(row['eventos_totales'])}",
            max_width=260
        ),
        tooltip=f"{row['country']}: {row['indice_riesgo']}",
    ).add_to(fg_indice)

fg_indice.add_to(mapa)

# ── 8. Marcadores clave ──────────────────────────────────
folium.Marker(
    location=[26.5, 56.3],
    popup="Estrecho de Ormuz",
    tooltip="Estrecho de Ormuz",
    icon=folium.Icon(color="white", icon="info-sign"),
).add_to(mapa)

# ── 9. Leyenda ───────────────────────────────────────────
leyenda_html = """
<div style="position: fixed; bottom: 30px; left: 30px; z-index: 1000;
     background-color: rgba(0,0,0,0.80); padding: 15px; border-radius: 8px;
     color: white; font-family: Arial; font-size: 11px; min-width: 230px;">
  <b style="font-size:13px;">Riesgo en Cables Submarinos</b><br>
  <i>Estrecho de Ormuz</i><br><br>

  <b>Índice de vulnerabilidad:</b><br>
  <span style="color:#ff2222;">&#9679;</span> Alto (&ge; 0.60)<br>
  <span style="color:#ff8800;">&#9679;</span> Medio-alto (0.45-0.59)<br>
  <span style="color:#ffdd00;">&#9679;</span> Medio (0.30-0.44)<br>
  <span style="color:#44bb44;">&#9679;</span> Bajo (&lt; 0.30)<br><br>

  <b>Heatmap:</b> Conflicto armado 2020-2026<br>
  <span style="color:#4444ff;">&#9632;</span> Bajo &nbsp;
  <span style="color:#ffdd00;">&#9632;</span> Medio &nbsp;
  <span style="color:#ff2222;">&#9632;</span> Alto<br><br>

  <b>Cables resaltados:</b> tocan la zona del Golfo<br>
  <i>Usa el control de capas (arriba derecha)</i>
</div>
"""
mapa.get_root().html.add_child(folium.Element(leyenda_html))
folium.LayerControl(collapsed=False).add_to(mapa)

# ── 10. Guardar ──────────────────────────────────────────
output_path = "outputs/mapa_completo.html"
mapa.save(output_path)
print(f"\nMapa guardado en: {output_path}")
print("Abre con: open outputs/mapa_completo.html\n")
