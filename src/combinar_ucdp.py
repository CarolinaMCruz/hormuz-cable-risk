"""
combinar_ucdp.py
Combina los 4 archivos UCDP GED en un dataset unificado.
Cubre 1989 - febrero 2026.
Output: data/processed/ucdp_combined.csv
"""

import pandas as pd
import os

ARCHIVOS = [
    "data/raw/GEDEvent_v25_1.csv",        # 1989-2024
    "data/raw/GEDEvent_v25_01_25_12.csv", # 2025
    "data/raw/GEDEvent_v26_0_1.csv",      # enero 2026
    "data/raw/GEDEvent_v26_0_2.csv",      # febrero 2026
]

ZONA = [
    "Iran", "Oman", "Yemen (North Yemen)", "Saudi Arabia",
    "United Arab Emirates", "Qatar", "Kuwait", "Bahrain",
    "Pakistan", "Iraq"
]

print("\n" + "="*55)
print("  COMBINANDO DATASETS UCDP")
print("="*55)

# ── 1. Verificar que existen los archivos ───────────────
print("\n[1] Verificando archivos...")
for f in ARCHIVOS:
    existe = os.path.exists(f)
    size = f"{os.path.getsize(f)/1e6:.1f} MB" if existe else "NO ENCONTRADO"
    print(f"    {'[OK]' if existe else '[FALTA]'} {f} ({size})")

# ── 2. Cargar y combinar ────────────────────────────────
print("\n[2] Cargando y combinando...")
dfs = []
for f in ARCHIVOS:
    if os.path.exists(f):
        df = pd.read_csv(f, low_memory=False)
        print(f"    {os.path.basename(f)}: {len(df):,} filas")
        dfs.append(df)

df_combined = pd.concat(dfs, ignore_index=True)
print(f"\n    Total combinado: {len(df_combined):,} filas")

# ── 3. Verificar duplicados ─────────────────────────────
print("\n[3] Verificando duplicados...")
duplicados = df_combined.duplicated(subset=["id"]).sum()
print(f"    Duplicados por id: {duplicados}")
if duplicados > 0:
    df_combined = df_combined.drop_duplicates(subset=["id"])
    print(f"    Eliminados. Filas finales: {len(df_combined):,}")

# ── 4. Verificar continuidad temporal ──────────────────
print("\n[4] Cobertura temporal:")
df_combined["date_start"] = pd.to_datetime(df_combined["date_start"])
print(f"    Desde: {df_combined['date_start'].min().date()}")
print(f"    Hasta: {df_combined['date_start'].max().date()}")
print(f"\n    Eventos por año (últimos 5):")
print(df_combined[df_combined["date_start"].dt.year >= 2021]
      .groupby(df_combined["date_start"].dt.year)
      .size().to_string())

# ── 5. Filtrar zona de interés ──────────────────────────
print("\n[5] Zona del Golfo / Ormuz:")
zona_df = df_combined[df_combined["country"].isin(ZONA)]
print(f"    Total eventos en zona: {len(zona_df):,}")
print(f"\n    Por país:")
print(zona_df["country"].value_counts().to_string())
print(f"\n    Por tipo de violencia:")
tipo_map = {1: "Conflicto estatal", 2: "Conflicto no estatal", 3: "Violencia unilateral"}
print(zona_df["type_of_violence"].map(tipo_map).value_counts().to_string())

# ── 6. Guardar dataset completo y filtrado ──────────────
print("\n[6] Guardando datasets...")
df_combined.to_csv("data/processed/ucdp_combined.csv", index=False)
zona_df.to_csv("data/processed/ucdp_gulf_zone.csv", index=False)
print(f"    ucdp_combined.csv  -> {len(df_combined):,} filas")
print(f"    ucdp_gulf_zone.csv -> {len(zona_df):,} filas")

print("\n" + "="*55)
print("  Datasets guardados en data/processed/")
print("="*55 + "\n")
