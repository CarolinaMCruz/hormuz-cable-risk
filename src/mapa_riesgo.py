"""
mapa_riesgo.py
Genera un mapa interactivo HTML con:
  - Landing points de cables submarinos en la zona del Golfo
  - Eventos de conflicto UCDP cercanos
  - Colores por nivel de concentración de riesgo

Output: outputs/mapa_riesgo.html
"""

import pandas as pd
import folium
from folium.plugins import HeatMap
import os

os.makedirs("outputs", exist_ok=True)

# ── 1. Cargar datos ─────────────────────────────────────
print("Cargando datos...")
df_landing = pd.read_csv("data/processed/landing_points.csv")
df_coords = pd.read_csv("data/processed/landing_points_coords.csv")
df_landing = df_landing.merge(df_coords, on="landing_id", how="left")
df_conflicto = pd.read_csv(
    "data/processed/ucdp_gulf_zone.csv", low_memory=False)

# ── 2. Filtrar landing points zona del Golfo ────────────
ZONA = [
    "Iran", "Oman", "Yemen (North Yemen)", "Saudi Arabia",
    "United Arab Emirates", "Qatar", "Kuwait", "Bahrain",
    "Pakistan", "Iraq"
]
lp_zona = df_landing[df_landing["country"].isin(ZONA)].copy()

cables_por_lp = df_landing.groupby(
    "landing_id").size().reset_index(name="n_cables")
lp_zona = lp_zona.merge(cables_por_lp, on="landing_id", how="left")

print(f"Landing points en zona: {len(lp_zona)}")

# ── 3. Filtrar conflictos con coordenadas ───────────────
df_conflicto = df_conflicto.dropna(subset=["latitude", "longitude"])
df_conflicto["date_start"] = pd.to_datetime(df_conflicto["date_start"])
conflicto_reciente = df_conflicto[df_conflicto["date_start"].dt.year >= 2020]
print(f"Eventos de conflicto recientes (2020-2026): {len(conflicto_reciente)}")

# ── 4. Crear mapa base ──────────────────────────────────
print("Generando mapa...")
mapa = folium.Map(
    location=[24.0, 57.0],
    zoom_start=5,
    tiles="CartoDB dark_matter"
)

# ── 5. Heatmap de conflictos ────────────────────────────
heat_data = conflicto_reciente[[
    "latitude", "longitude", "best"]].values.tolist()
HeatMap(
    heat_data,
    name="Intensidad de conflicto (2020-2026)",
    min_opacity=0.3,
    radius=20,
    blur=15,
    gradient={0.2: "blue", 0.5: "yellow", 0.8: "orange", 1.0: "red"},
).add_to(mapa)

# ── 6. Landing points ───────────────────────────────────
colores_pais = {
    "Iran": "red",
    "Iraq": "orange",
    "Yemen (North Yemen)": "darkred",
    "Saudi Arabia": "green",
    "United Arab Emirates": "blue",
    "Oman": "lightblue",
    "Qatar": "purple",
    "Kuwait": "pink",
    "Bahrain": "cadetblue",
    "Pakistan": "darkgreen",
}

fg_landing = folium.FeatureGroup(name="Landing Points de cables")

for _, row in lp_zona.iterrows():
    if pd.isna(row["latitude"]) or pd.isna(row["longitude"]):
        continue

    color = colores_pais.get(row["country"], "gray")
    n = row.get("n_cables", 1)
    radio = 4 + (n * 2)

    folium.CircleMarker(
        location=[row["latitude"], row["longitude"]],
        radius=radio,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.8,
        popup=folium.Popup(
            f"<b>{row['landing_name']}</b><br>"
            f"País: {row['country']}<br>"
            f"Cables: {n}<br>"
            f"ID: {row['landing_id']}",
            max_width=250
        ),
        tooltip=f"{row['landing_name']} ({n} cables)",
    ).add_to(fg_landing)

fg_landing.add_to(mapa)

# ── 7. Eventos de conflicto recientes como puntos ───────
fg_conflicto = folium.FeatureGroup(
    name="Eventos de conflicto (2023-2026)", show=False)

conflicto_2023 = df_conflicto[df_conflicto["date_start"].dt.year >= 2023]
for _, row in conflicto_2023.iterrows():
    folium.CircleMarker(
        location=[row["latitude"], row["longitude"]],
        radius=3,
        color="yellow",
        fill=True,
        fill_opacity=0.5,
        popup=folium.Popup(
            f"<b>{row['conflict_name']}</b><br>"
            f"País: {row['country']}<br>"
            f"Fecha: {str(row['date_start'])[:10]}<br>"
            f"Muertes estimadas: {row['best']}",
            max_width=250
        ),
    ).add_to(fg_conflicto)

fg_conflicto.add_to(mapa)

# ── 8. Marcador del Estrecho de Ormuz ───────────────────
folium.Marker(
    location=[26.5, 56.3],
    popup="Estrecho de Ormuz",
    tooltip="Estrecho de Ormuz",
    icon=folium.Icon(color="white", icon="info-sign"),
).add_to(mapa)

# ── 9. Leyenda ──────────────────────────────────────────
leyenda_html = """
<div style="position: fixed; bottom: 30px; left: 30px; z-index: 1000;
     background-color: rgba(0,0,0,0.7); padding: 15px; border-radius: 8px;
     color: white; font-family: Arial; font-size: 12px;">
  <b>Mapa de Riesgo - Cables Submarinos</b><br>
  <b>Estrecho de Ormuz</b><br><br>
  <b>Landing Points por país:</b><br>
  <span style="color:#ff4444;">&#9679;</span> Iran<br>
  <span style="color:#ffa500;">&#9679;</span> Iraq<br>
  <span style="color:#8b0000;">&#9679;</span> Yemen<br>
  <span style="color:#00aa00;">&#9679;</span> Saudi Arabia<br>
  <span style="color:#4444ff;">&#9679;</span> UAE<br>
  <span style="color:#add8e6;">&#9679;</span> Oman<br>
  <span style="color:#800080;">&#9679;</span> Qatar<br>
  <span style="color:#ffc0cb;">&#9679;</span> Kuwait / Bahrain<br>
  <span style="color:#006400;">&#9679;</span> Pakistan<br><br>
  <i>Tamaño del círculo = número de cables</i><br><br>
  <b>Heatmap:</b> Intensidad de conflicto 2020-2026<br>
  <span style="color:blue;">&#9632;</span> Baja &nbsp;
  <span style="color:yellow;">&#9632;</span> Media &nbsp;
  <span style="color:red;">&#9632;</span> Alta
</div>
"""
mapa.get_root().html.add_child(folium.Element(leyenda_html))

# ── 10. Control de capas ────────────────────────────────
folium.LayerControl().add_to(mapa)

# ── 11. Guardar ─────────────────────────────────────────
output_path = "outputs/mapa_riesgo.html"
mapa.save(output_path)
print(f"\nMapa guardado en: {output_path}")
print("Abre con: open outputs/mapa_riesgo.html\n")
