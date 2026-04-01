"""
construir_dataset.py
Itera sobre todos los cables de TeleGeography y construye
dos CSVs limpios:
  - cables.csv        : un cable por fila con sus metadatos
  - landing_points.csv: un punto de aterrizaje por fila con país y cables asociados

ADVERTENCIA: hace ~691 requests HTTP. Tarda entre 3 y 8 minutos.
"""

import requests
import pandas as pd
import time

BASE = "https://www.submarinecablemap.com/api/v3"

# ─────────────────────────────────────────────
# 1. DESCARGAR LISTA MAESTRA DE CABLES
# ─────────────────────────────────────────────
print("\n[1] Descargando lista maestra de cables...")
r = requests.get(f"{BASE}/cable/all.json", timeout=15)
cables_lista = r.json()
print(f"    Total cables: {len(cables_lista)}")

# ─────────────────────────────────────────────
# 2. ITERAR Y ENRIQUECER CADA CABLE
# ─────────────────────────────────────────────
print("\n[2] Descargando detalle de cada cable (esto tarda unos minutos)...")

cables_rows = []
landing_rows = []
errores = []

for i, cable in enumerate(cables_lista):
    cable_id = cable["id"]

    try:
        r = requests.get(f"{BASE}/cable/{cable_id}.json", timeout=10)
        r.raise_for_status()
        d = r.json()

        # Fila para cables.csv
        cables_rows.append({
            "id":          d.get("id"),
            "name":        d.get("name"),
            "length":      d.get("length"),
            "owners":      d.get("owners"),
            "suppliers":   d.get("suppliers"),
            "rfs":         d.get("rfs"),
            "rfs_year":    d.get("rfs_year"),
            "is_planned":  d.get("is_planned"),
            "url":         d.get("url"),
            "notes":       d.get("notes"),
            "n_landing_points": len(d.get("landing_points", [])),
            "countries": ", ".join(sorted(set(
                lp["country"] for lp in d.get("landing_points", [])
                if lp.get("country")
            ))),
        })

        # Filas para landing_points.csv (una por landing point del cable)
        for lp in d.get("landing_points", []):
            landing_rows.append({
                "landing_id":   lp.get("id"),
                "landing_name": lp.get("name"),
                "country":      lp.get("country"),
                "cable_id":     d.get("id"),
                "cable_name":   d.get("name"),
                "rfs_year":     d.get("rfs_year"),
                "is_planned":   d.get("is_planned"),
            })

    except Exception as e:
        errores.append({"id": cable_id, "error": str(e)})

    # Progreso cada 50 cables
    if (i + 1) % 50 == 0:
        print(f"    Procesados: {i+1}/{len(cables_lista)}")

    time.sleep(0.05)  # pausa para no saturar el servidor

print(f"    Completado. Errores: {len(errores)}")

# ─────────────────────────────────────────────
# 3. CONSTRUIR Y GUARDAR DATAFRAMES
# ─────────────────────────────────────────────
print("\n[3] Construyendo datasets...")

df_cables = pd.DataFrame(cables_rows)
df_landing = pd.DataFrame(landing_rows)

# Guardar CSVs
df_cables.to_csv("cables.csv", index=False)
df_landing.to_csv("landing_points.csv", index=False)
print(f"    cables.csv       -> {len(df_cables)} filas")
print(f"    landing_points.csv -> {len(df_landing)} filas")

# ─────────────────────────────────────────────
# 4. RESUMEN DE LA ZONA DE INTERÉS
# ─────────────────────────────────────────────
zona = ["Iran", "Oman", "United Arab Emirates", "Yemen",
        "Saudi Arabia", "Qatar", "Kuwait", "Bahrain",
        "Pakistan", "India", "Iraq"]

print("\n[4] Cables que tocan la zona del Golfo / Estrecho de Ormuz:")
zona_cables = df_landing[df_landing["country"].isin(zona)]

print(f"\n    Puntos de aterrizaje en zona: {len(zona_cables)}")
print(f"\n    Por país:")
print(zona_cables["country"].value_counts().to_string())

print(f"\n    Cables activos en zona (no planificados):")
activos = zona_cables[zona_cables["is_planned"] == False]
resumen = (
    activos.groupby("cable_name")["country"]
    .apply(lambda x: ", ".join(sorted(set(x))))
    .reset_index()
)
resumen.columns = ["cable", "paises_en_zona"]
print(resumen.to_string(index=False))

print("\n" + "="*55)
print("  Dataset construido. Archivos guardados:")
print("    cables.csv")
print("    landing_points.csv")
print("="*55 + "\n")
