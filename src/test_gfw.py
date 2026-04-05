"""
test_gfw.py
Versión FINAL - Corrección de error de validación 422 (date-range).
"""

import requests

GFW_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImtpZEtleSJ9.eyJkYXRhIjp7Im5hbWUiOiJzdWJtYXJpbmUtY2FibGUtcmlzayIsInVzZXJJZCI6NTg2NzIsImFwcGxpY2F0aW9uTmFtZSI6InN1Ym1hcmluZS1jYWJsZS1yaXNrIiwiaWQiOjUzMzcsInR5cGUiOiJ1c2VyLWFwcGxpY2F0aW9uIn0sImlhdCI6MTc3NTAxNDQ4MSwiZXhwIjoyMDkwMzc0NDgxLCJhdWQiOiJnZnciLCJpc3MiOiJnZncifQ.gJ3_eik4TFeAZU2ljI2OuHDwDrLIy25vilm2tI4dL62iQLi6FrJNS7UtTi4_Loru5ecgyAsmYNY-7jhGpITC9KgmqfnwkQuCQJbTxEFgsZo8R15pCKLHKljJBMe98GdUoIdOWorWK5I2wdirCl37gMcho_zJQwmwW9P0OUn27x5sWAAoSxyfELOm1itkrxJ4FYdIyKWoXatww4tCaNCUy_8ugqX2qbB1yRd3mS36GkLtydh1shTVUte4rzk35kxyQ-KbGwAhBt_Mz72vGHl1DFdufqxmo-gI4USRxIJdBb6iBkftBOPxw-yxYv0bKp3Jk6EudTz8gEUb97fK67bXcjW7icjPaGLuk7wTc032L5VdC0YpsFODfR7F7qU1_bSJNxBqbVSsEoQRJxL-R_lX0MyWjFJtIWsMvfnimy50u3529U1uTRijkNO6zI9Yi_p3O6Fu9wzHyemC6V-_Fe4qWfQlNHJ1BxZZG2VYFd94d4Tx61V-Gf4avK9VtMwrbYwR"

BASE = "https://gateway.api.globalfishingwatch.org"

headers = {
    "Authorization": f"Bearer {GFW_TOKEN}",
    "Content-Type": "application/json",
}

print("\n[6] Probando 4Wings AIS vessel presence...")

url = f"{BASE}/v3/4wings/report"

# 1. PARÁMETROS DE URL (Query Params)
# Es obligatorio usar el índice  en datasets
params = {
    "datasets": "public-global-presence:latest",
    "date-range": "2024-01-01,2024-02-01",
    "spatial-resolution": "LOW",
    "temporal-resolution": "MONTHLY",
    "group-by": "FLAG",
    "format": "JSON",
}

# 2. CUERPO DE LA PETICIÓN (Body)
# Solo debe contener la geometría. No incluyas resoluciones ni grupos aquí.
payload = {
    "geojson": {
        "type": "Polygon",
        "coordinates": [[
            [55.8, 25.7],
            [57.2, 25.7],
            [57.2, 26.8],
            [55.8, 26.8],
            [55.8, 25.7]
        ]]
    }
}

r = requests.post(
    url,
    headers=headers,
    params=params,
    json=payload,
    timeout=20
)

print(f"    Status: {r.status_code}")
if r.status_code in [7, 8]:
    print("    [OK] 4Wings API funciona")
    print(f"    Respuesta: {list(r.json().keys())}")
else:
    print(f"    [ERROR] {r.text}")

print("Prueba completada")
