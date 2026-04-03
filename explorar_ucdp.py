"""
explorar_ucdp.py
Exploración inicial del dataset UCDP GED v25.1
Identifica eventos de conflicto relevantes para la zona del Golfo / Estrecho de Ormuz.
"""

import pandas as pd

ARCHIVO = "data/raw/GEDEvent_v25_1.csv"
ZONA = ["Iran", "Oman", "Yemen (North Yemen)", "Saudi Arabia", "United Arab Emirates",
        "Qatar", "Kuwait", "Bahrain", "Pakistan", "Iraq"]

print("\n" + "="*55)
print("  EXPLORACIÓN - UCDP GED v25.1")
print("="*55)

# ── 1. Carga ────────────────────────────────────────────
print("\n[1] Cargando dataset...")
df = pd.read_csv(ARCHIVO, low_memory=False)
print(f"    Filas:    {len(df):,}")
print(f"    Columnas: {len(df.columns)}")
print(f"\n    Columnas disponibles:")
for col in df.columns:
    print(f"      - {col}")

# ── 2. Muestra de un registro ───────────────────────────
print("\n[2] Primer registro:")
print(df.iloc[0].to_string())

# ── 3. Rango temporal ───────────────────────────────────
if "year" in df.columns:
    print(f"\n[3] Rango de años: {df['year'].min()} - {df['year'].max()}")

# ── 4. Filtro zona de interés ───────────────────────────
print("\n[4] Eventos en zona del Golfo / Ormuz:")

col_pais = None
for candidato in ["country", "country_id", "side_a", "where_prec"]:
    if candidato in df.columns:
        col_pais = candidato
        break

if col_pais:
    zona_df = df[df[col_pais].isin(ZONA)]
    print(f"    Usando columna: '{col_pais}'")
    print(f"    Eventos en zona: {len(zona_df):,}")
    print(f"\n    Por país:")
    print(zona_df[col_pais].value_counts().to_string())
else:
    print("    Columna de país no identificada. Columnas disponibles:")
    print(df.columns.tolist())

# ── 5. Verificar coordenadas ────────────────────────────
print("\n[5] Verificando columnas de coordenadas:")
coord_cols = [c for c in df.columns if any(
    x in c.lower() for x in ["lat", "lon", "geo", "coord"])]
print(f"    {coord_cols}")
if coord_cols:
    print(f"\n    Muestra de coordenadas:")
    print(df[coord_cols].dropna().head(3).to_string())

print("\n" + "="*55)
print("  Exploración completada")
print("="*55 + "\n")
