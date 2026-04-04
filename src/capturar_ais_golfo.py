"""
capturar_ais_golfo.py
Descarga datos de presencia AIS de Global Fishing Watch para:
  - Golfo Pérsico
  - Estrecho de Ormuz
  - Golfo de Omán

Dos períodos para comparación:
  - Período 1: diciembre 2025 - enero 2026 (pre-conflicto)
  - Período 2: febrero 2026 - marzo 2026 (conflicto activo)

Output:
  data/processed/ais_periodo1.csv  (dic2025-ene2026)
  data/processed/ais_periodo2.csv  (feb2026-mar2026)
"""

import asyncio
import gfwapiclient as gfw
import os

GFW_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImtpZEtleSJ9.eyJkYXRhIjp7Im5hbWUiOiJzdWJtYXJpbmUtY2FibGUtcmlzayIsInVzZXJJZCI6NTg2NzIsImFwcGxpY2F0aW9uTmFtZSI6InN1Ym1hcmluZS1jYWJsZS1yaXNrIiwiaWQiOjUzMzcsInR5cGUiOiJ1c2VyLWFwcGxpY2F0aW9uIn0sImlhdCI6MTc3NTAxNDQ4MSwiZXhwIjoyMDkwMzc0NDgxLCJhdWQiOiJnZnciLCJpc3MiOiJnZncifQ.gJ3_eik4TFeAZU2ljI2OuHDwDrLIy25vilm2tI4dL62iQLi6FrJNS7UtTi4_Loru5ecgyAsmYNY-7jhGpITC9KgmqfnwkQuCQJbTxEFgsZo8R15pCKLHKljJBMe98GdUoIdOWorWK5I2wdirCl37gMcho_zJQwmwW9P0OUn27x5sWAAoSxyfELOm1itkrxJ4FYdIyKWoXatww4tCaNCUy_8ugqX2qbB1yRd3mS36GkLtydh1shTVUte4rzk35kxyQ-KbGwAhBt_Mz72vGHl1DFdufqxmo-gI4USRxIJdBb6iBkftBOPxw-yxYv0bKp3Jk6EudTz8gEUb97fK67bXcjW7icjPaGLuk7wTc032L5VdC0YpsFODfR7F7qU1_bSJNxBqbVSsEoQRJxL-R_lX0MyWjFJtIWsMvfnimy50u3529U1uTRijkNO6zI9Yi_p3O6Fu9wzHyemC6V-_Fe4qWfQlNHJ1BxZZG2VYFd94d4Tx61V-Gf4avK9VtMwrbYwR"  # reemplaza con tu token

os.makedirs("data/processed", exist_ok=True)

# Polígono preciso del Golfo Pérsico + Estrecho de Ormuz + Golfo de Omán
GEOJSON = {
    "type": "Polygon",
    "coordinates": [[
        [59.896358407, 22.3816106839],
        [59.0545699737, 23.0450761811],
        [58.5650806553, 23.538255411],
        [57.8471629883, 23.7430904163],
        [57.0328458943, 24.0324815525],
        [56.5134456265, 24.559486901],
        [56.4589446424, 24.8320761446],
        [56.234845111, 25.7450725378],
        [56.4021705412, 26.3074510024],
        [55.3113086317, 25.2672273818],
        [54.4958260869, 24.5540447615],
        [54.2414248357, 23.9979591894],
        [53.3671702742, 24.029440307],
        [52.5283787143, 24.0753554487],
        [52.1072805982, 23.9551558533],
        [51.8192697605, 24.0148636725],
        [51.3042012872, 24.3277978327],
        [51.524013943, 24.871893994],
        [51.6424157476, 25.268304281],
        [51.5198440183, 25.3226081821],
        [51.4225324098, 25.5463088277],
        [51.5520807439, 25.773745134],
        [51.5619843151, 25.9023233463],
        [51.3984751519, 25.9812485497],
        [51.3001210623, 26.1227772168],
        [51.1613908747, 26.1439431734],
        [51.0246654586, 25.980960203],
        [50.9357738905, 25.7340211624],
        [50.8607954365, 25.4892825603],
        [50.7522170122, 25.2604358117],
        [50.8149663601, 24.9602938357],
        [50.8668899418, 24.8438444568],
        [50.7630427783, 24.7050313711],
        [50.4243165863, 25.4250594402],
        [50.209044223, 25.6511720631],
        [49.9612825669, 26.1673319659],
        [50.2224360966, 26.1531930753],
        [50.2494203209, 26.4405088868],
        [50.0832247638, 26.481465025],
        [50.0005880828, 26.6745264637],
        [50.1355492999, 26.6957347357],
        [49.733793092, 26.9084223755],
        [49.5534839436, 27.1700897853],
        [49.4308721189, 27.1192469072],
        [49.1287007928, 27.3869815716],
        [49.2680445779, 27.4942235084],
        [49.0274319029, 27.6070195354],
        [48.8735879847, 27.5855943334],
        [48.4266820762, 28.4835489336],
        [48.1756846849, 28.9548729262],
        [48.0395206048, 29.3010217492],
        [47.9639407194, 29.3922412622],
        [47.7999103155, 29.2850412002],
        [47.6745720016, 29.3413291728],
        [47.8055637712, 29.475944428],
        [47.9611741347, 29.6031999076],
        [48.1394785116, 29.551417049],
        [47.8306132014, 29.8930382295],
        [49.1107776127, 30.4364354656],
        [49.937914665, 30.2801293716],
        [50.6997904493, 29.4118495459],
        [50.976556952, 29.0078536692],
        [51.3930631829, 28.0342851333],
        [52.6227802257, 27.5495643765],
        [53.7769094621, 26.8375540627],
        [54.52912468, 26.6211933116],
        [56.1932218696, 27.1883518512],
        [56.8488711675, 27.115760711],
        [57.0509936276, 26.5958872349],
        [57.2256447483, 25.9224995534],
        [58.8134881597, 25.527272806],
        [61.0551494464, 25.2874012886],
        [61.6147323033, 25.1730884037],
        [59.896358407, 22.3816106839],
    ]]
}

PERIODOS = [
    {
        "nombre": "periodo1_dic2025_ene2026",
        "start_date": "2025-12-01",
        "end_date": "2026-01-31",
        "descripcion": "Pre-conflicto (dic 2025 - ene 2026)",
        "output": "data/processed/ais_periodo1.csv",
    },
    {
        "nombre": "periodo2_feb2026_mar2026",
        "start_date": "2026-02-01",
        "end_date": "2026-03-31",
        "descripcion": "Conflicto activo (feb 2026 - mar 2026)",
        "output": "data/processed/ais_periodo2.csv",
    },
]


async def descargar_periodo(client, periodo):
    print(f"\n  Descargando: {periodo['descripcion']}")
    print(f"  Rango: {periodo['start_date']} a {periodo['end_date']}")

    result = await client.fourwings.create_ais_presence_report(
        start_date=periodo["start_date"],
        end_date=periodo["end_date"],
        spatial_resolution="LOW",
        temporal_resolution="MONTHLY",
        group_by="FLAG",
        geojson=GEOJSON,
    )

    df = result.df()
    df.to_csv(periodo["output"], index=False)
    print(f"  Registros: {len(df):,}")
    print(f"  Guardado: {periodo['output']}")
    return df


async def main():
    print("\n" + "="*55)
    print("  CAPTURA AIS - Golfo Pérsico / Ormuz / Golfo de Omán")
    print("="*55)

    client = gfw.Client(access_token=GFW_TOKEN)

    for periodo in PERIODOS:
        try:
            df = await descargar_periodo(client, periodo)
            print(f"  Embarcaciones únicas: {df['flag'].nunique()} banderas")
            print(f"  Horas totales de presencia: {df['hours'].sum():,.0f}")
        except Exception as e:
            print(f"  [ERROR] {periodo['nombre']}: {e}")

        # Pausa entre requests para evitar rate limit
        print("  Esperando 10 segundos antes del siguiente request...")
        await asyncio.sleep(10)

    print("\n" + "="*55)
    print("  Descarga completada")
    print("="*55 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
