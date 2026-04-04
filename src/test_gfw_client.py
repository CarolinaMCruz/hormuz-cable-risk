"""
test_gfw_client.py
Prueba de conexión a Global Fishing Watch usando el cliente oficial de Python.
Obtiene presencia de embarcaciones en el Estrecho de Ormuz.
"""

import asyncio
import gfwapiclient as gfw

GFW_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImtpZEtleSJ9.eyJkYXRhIjp7Im5hbWUiOiJzdWJtYXJpbmUtY2FibGUtcmlzayIsInVzZXJJZCI6NTg2NzIsImFwcGxpY2F0aW9uTmFtZSI6InN1Ym1hcmluZS1jYWJsZS1yaXNrIiwiaWQiOjUzMzcsInR5cGUiOiJ1c2VyLWFwcGxpY2F0aW9uIn0sImlhdCI6MTc3NTAxNDQ4MSwiZXhwIjoyMDkwMzc0NDgxLCJhdWQiOiJnZnciLCJpc3MiOiJnZncifQ.gJ3_eik4TFeAZU2ljI2OuHDwDrLIy25vilm2tI4dL62iQLi6FrJNS7UtTi4_Loru5ecgyAsmYNY-7jhGpITC9KgmqfnwkQuCQJbTxEFgsZo8R15pCKLHKljJBMe98GdUoIdOWorWK5I2wdirCl37gMcho_zJQwmwW9P0OUn27x5sWAAoSxyfELOm1itkrxJ4FYdIyKWoXatww4tCaNCUy_8ugqX2qbB1yRd3mS36GkLtydh1shTVUte4rzk35kxyQ-KbGwAhBt_Mz72vGHl1DFdufqxmo-gI4USRxIJdBb6iBkftBOPxw-yxYv0bKp3Jk6EudTz8gEUb97fK67bXcjW7icjPaGLuk7wTc032L5VdC0YpsFODfR7F7qU1_bSJNxBqbVSsEoQRJxL-R_lX0MyWjFJtIWsMvfnimy50u3529U1uTRijkNO6zI9Yi_p3O6Fu9wzHyemC6V-_Fe4qWfQlNHJ1BxZZG2VYFd94d4Tx61V-Gf4avK9VtMwrbYwR"
# reemplaza con tu token

# Bounding box del Estrecho de Ormuz
GEOJSON = {
    "type": "Polygon",
    "coordinates": [[
        [55.8, 25.7],
        [57.2, 25.7],
        [57.2, 26.8],
        [55.8, 26.8],
        [55.8, 25.7],
    ]]
}


async def main():
    print("\n" + "="*55)
    print("  GFW - Presencia de embarcaciones en Ormuz")
    print("="*55)

    client = gfw.Client(access_token=GFW_TOKEN)

    print("\n[1] Solicitando datos de presencia AIS...")
    try:
        result = await client.fourwings.create_ais_presence_report(
            start_date="2026-02-28",
            end_date="2026-04-01",
            spatial_resolution="LOW",
            temporal_resolution="MONTHLY",
            group_by="FLAG",
            geojson=GEOJSON,
        )
        print(f"    [OK] Datos recibidos")
        print(f"\n    DataFrame:")
        print(result.df())

    except Exception as e:
        print(f"    [ERROR] {e}")


if __name__ == "__main__":
    asyncio.run(main())
