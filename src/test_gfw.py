"""
test_gfw.py
Prueba corregida de conexion a Global Fishing Watch API.
Usa el endpoint de vessel presence con parametros correctos.
"""

import requests

GFW_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImtpZEtleSJ9.eyJkYXRhIjp7Im5hbWUiOiJzdWJtYXJpbmUtY2FibGUtcmlzayIsInVzZXJJZCI6NTg2NzIsImFwcGxpY2F0aW9uTmFtZSI6InN1Ym1hcmluZS1jYWJsZS1yaXNrIiwiaWQiOjUzMzcsInR5cGUiOiJ1c2VyLWFwcGxpY2F0aW9uIn0sImlhdCI6MTc3NTAxNDQ4MSwiZXhwIjoyMDkwMzc0NDgxLCJhdWQiOiJnZnciLCJpc3MiOiJnZncifQ.gJ3_eik4TFeAZU2ljI2OuHDwDrLIy25vilm2tI4dL62iQLi6FrJNS7UtTi4_Loru5ecgyAsmYNY-7jhGpITC9KgmqfnwkQuCQJbTxEFgsZo8R15pCKLHKljJBMe98GdUoIdOWorWK5I2wdirCl37gMcho_zJQwmwW9P0OUn27x5sWAAoSxyfELOm1itkrxJ4FYdIyKWoXatww4tCaNCUy_8ugqX2qbB1yRd3mS36GkLtydh1shTVUte4rzk35kxyQ-KbGwAhBt_Mz72vGHl1DFdufqxmo-gI4USRxIJdBb6iBkftBOPxw-yxYv0bKp3Jk6EudTz8gEUb97fK67bXcjW7icjPaGLuk7wTc032L5VdC0YpsFODfR7F7qU1_bSJNxBqbVSsEoQRJxL-R_lX0MyWjFJtIWsMvfnimy50u3529U1uTRijkNO6zI9Yi_p3O6Fu9wzHyemC6V-_Fe4qWfQlNHJ1BxZZG2VYFd94d4Tx61V-Gf4avK9VtMwrbYwR"   # pega tu token aqui

BASE = "https://gateway.api.globalfishingwatch.org"

headers = {
    "Authorization": f"Bearer {GFW_TOKEN}",
    "Content-Type": "application/json",
}

# ── Prueba 1: Vessel search (mas simple) ──────────────
print("\n[1] Probando Vessels API...")
r = requests.get(
    f"{BASE}/v3/vessels/search",
    headers=headers,
    params={
        "query": "fishing",
        "datasets[0]": "public-global-vessel-identity:latest",
        "limit": 3,
    },
    timeout=15,
)
print(f"    Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    print(f"    [OK] Vessels API funciona")
    print(f"    Claves en respuesta: {list(data.keys())}")
else:
    print(f"    [ERROR] {r.text[:300]}")


# ── Prueba 2: 4Wings con datasets como query params ───
print("\n[2] Probando 4Wings AIS vessel presence...")
params = {
    "datasets[0]": "public-global-vessel-presence:latest",
    "start-date": "2024-01-01",
    "end-date": "2024-01-07",
    "spatial-resolution": "LOW",
    "temporal-resolution": "YEARLY",
    "group-by": "FLAG",
}

# Bounding box del Estrecho de Ormuz
payload = {
    "geometry": {
        "type": "Polygon",
        "coordinates": [[
            [55.8, 25.7],
            [57.2, 25.7],
            [57.2, 26.8],
            [55.8, 26.8],
            [55.8, 25.7],
        ]]
    }
}

r = requests.post(
    f"{BASE}/v3/4wings/report",
    headers=headers,
    params=params,
    json=payload,
    timeout=20,
)
print(f"    Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    print(f"    [OK] 4Wings API funciona")
    print(f"    Claves en respuesta: {list(data.keys())}")
else:
    print(f"    [ERROR] {r.text[:300]}")


print("\nPrueba completada.\n")
