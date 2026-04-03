"""
capturar_ais.py
Captura tráfico de embarcaciones AIS en tiempo real en el Estrecho de Ormuz.
Guarda los datos en data/processed/ais_ormuz.csv

Uso:
    python src/capturar_ais.py --minutos 5

El script captura durante el tiempo indicado y guarda el resultado.
"""

import asyncio
import websockets
import json
import csv
import os
import argparse
from datetime import datetime

# ── Configuración ───────────────────────────────────────
API_KEY = "e29ed0eca7ecf8c3715ed81365c308849fd54685"  # reemplaza con tu key

# Bounding box del Estrecho de Ormuz y Golfo Pérsico
# [lat_min, lon_min], [lat_max, lon_max]
BOUNDING_BOX = [[22.0, 55.0], [28.0, 60.0]]

OUTPUT_FILE = "data/processed/ais_ormuz.csv"
os.makedirs("data/processed", exist_ok=True)

# Columnas a guardar
COLUMNAS = [
    "timestamp", "mmsi", "ship_name", "ship_type",
    "latitude", "longitude", "speed", "course",
    "destination", "status"
]

# ── Parser de argumentos ────────────────────────────────
parser = argparse.ArgumentParser()
parser.add_argument("--minutos", type=int, default=2,
                    help="Duración de captura en minutos (default: 2)")
args = parser.parse_args()

DURACION_SEGUNDOS = args.minutos * 60


async def capturar():
    url = "wss://stream.aisstream.io/v0/stream"

    subscription = {
        "APIkey": API_KEY,
        "BoundingBoxes": [BOUNDING_BOX],
        "FilterMessageTypes": ["PositionReport", "ShipStaticData"]
    }

    registros = []
    inicio = asyncio.get_event_loop().time()

    print(f"\n{'='*55}")
    print(f"  CAPTURA AIS - Estrecho de Ormuz")
    print(f"{'='*55}")
    print(f"  Zona: {BOUNDING_BOX}")
    print(f"  Duración: {args.minutos} minuto(s)")
    print(f"  Iniciando...\n")

    try:
        async with websockets.connect(url) as ws:
            await ws.send(json.dumps(subscription))
            response = await asyncio.wait_for(ws.recv(), timeout=10.0)
            print(f"  Respuesta del servidor: {response}")

            while True:
                elapsed = asyncio.get_event_loop().time() - inicio
                if elapsed >= DURACION_SEGUNDOS:
                    break

                try:
                    msg = await asyncio.wait_for(ws.recv(), timeout=5.0)
                    data = json.loads(msg)

                    msg_type = data.get("MessageType", "")
                    meta = data.get("MetaData", {})
                    msg_data = data.get("Message", {})

                    registro = {
                        "timestamp":  datetime.utcnow().isoformat(),
                        "mmsi":       meta.get("MMSI", ""),
                        "ship_name":  meta.get("ShipName", "").strip(),
                        "latitude":   meta.get("latitude", ""),
                        "longitude":  meta.get("longitude", ""),
                        "ship_type":  "",
                        "speed":      "",
                        "course":     "",
                        "destination": "",
                        "status":     "",
                    }

                    if msg_type == "PositionReport":
                        pos = msg_data.get("PositionReport", {})
                        registro["speed"] = pos.get("Sog", "")
                        registro["course"] = pos.get("Cog", "")
                        registro["status"] = pos.get("NavigationalStatus", "")

                    elif msg_type == "ShipStaticData":
                        static = msg_data.get("ShipStaticData", {})
                        registro["ship_type"] = static.get("Type", "")
                        registro["destination"] = static.get(
                            "Destination", "").strip()

                    registros.append(registro)

                    if len(registros) % 10 == 0:
                        print(f"  Embarcaciones capturadas: {len(registros)}")

                except asyncio.TimeoutError:
                    continue

    except Exception as e:
        print(f"  Error de conexión: {e}")

    # ── Guardar resultados ──────────────────────────────
    print(f"\n  Total embarcaciones capturadas: {len(registros)}")

    if registros:
        file_exists = os.path.isfile(OUTPUT_FILE)
        with open(OUTPUT_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=COLUMNAS)
            if not file_exists:
                writer.writeheader()
            writer.writerows(registros)
        print(f"  Guardado en: {OUTPUT_FILE}")

        # Resumen
        import pandas as pd
        df = pd.read_csv(OUTPUT_FILE)
        print(f"\n  Resumen del archivo acumulado:")
        print(f"  Total registros: {len(df)}")
        print(f"  Embarcaciones únicas: {df['mmsi'].nunique()}")
        if "ship_type" in df.columns:
            print(f"\n  Por tipo de embarcación:")
            print(df[df["ship_type"] != ""]
                  ["ship_type"].value_counts().head(10).to_string())
        if "destination" in df.columns:
            print(f"\n  Destinos más frecuentes:")
            print(df[df["destination"] != ""]
                  ["destination"].value_counts().head(10).to_string())
    else:
        print("  Sin datos capturados. Verifica tu API key.")

    print(f"\n{'='*55}\n")


if __name__ == "__main__":
    asyncio.run(capturar())
