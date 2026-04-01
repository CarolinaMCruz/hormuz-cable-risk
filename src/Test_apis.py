"""
test_apis.py
Prueba de conexión a las tres fuentes de datos del proyecto:
  1. TeleGeography  - sin credenciales (API pública)
  2. ACLED          - OAuth con email + password (acleddata.com)
  3. Global Fishing Watch - token Bearer (globalfishingwatch.org)

Instrucciones:
  pip install requests
  python test_apis.py

Coloca tus credenciales en las variables de la sección CONFIGURACIÓN.
"""

import requests

# ─────────────────────────────────────────────
# CONFIGURACIÓN  (edita aquí tus credenciales)
# ─────────────────────────────────────────────
ACLED_USERNAME = "carolinam.cruz87@gmail.com"
# cambia esto después de cambiar tu contraseña
ACLED_PASSWORD = "LYWW7N@t%s4i!n*"

GFW_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImtpZEtleSJ9.eyJkYXRhIjp7Im5hbWUiOiJzdWJtYXJpbmUtY2FibGUtcmlzayIsInVzZXJJZCI6NTg2NzIsImFwcGxpY2F0aW9uTmFtZSI6InN1Ym1hcmluZS1jYWJsZS1yaXNrIiwiaWQiOjUzMzcsInR5cGUiOiJ1c2VyLWFwcGxpY2F0aW9uIn0sImlhdCI6MTc3NTAxNDQ4MSwiZXhwIjoyMDkwMzc0NDgxLCJhdWQiOiJnZnciLCJpc3MiOiJnZncifQ.gJ3_eik4TFeAZU2ljI2OuHDwDrLIy25vilm2tI4dL62iQLi6FrJNS7UtTi4_Loru5ecgyAsmYNY-7jhGpITC9KgmqfnwkQuCQJbTxEFgsZo8R15pCKLHKljJBMe98GdUoIdOWorWK5I2wdirCl37gMcho_zJQwmwW9P0OUn27x5sWAAoSxyfELOm1itkrxJ4FYdIyKWoXatww4tCaNCUy_8ugqX2qbB1yRd3mS36GkLtydh1shTVUte4rzk35kxyQ-KbGwAhBt_Mz72vGHl1DFdufqxmo-gI4USRxIJdBb6iBkftBOPxw-yxYv0bKp3Jk6EudTz8gEUb97fK67bXcjW7icjPaGLuk7wTc032L5VdC0YpsFODfR7F7qU1_bSJNxBqbVSsEoQRJxL-R_lX0MyWjFJtIWsMvfnimy50u3529U1uTRijkNO6zI9Yi_p3O6Fu9wzHyemC6V-_Fe4qWfQlNHJ1BxZZG2VYFd94d4Tx61V-Gf4avK9VtMwrbYwR"  # ─────────────────────────────────────────────


def separador(titulo):
    print("\n" + "=" * 55)
    print(f"  {titulo}")
    print("=" * 55)


# ─────────────────────────────────────────────
# 1. TELEGEOGRAPHY  (sin autenticación)
# ─────────────────────────────────────────────
def test_telegeography():
    separador("1. TeleGeography - Cables submarinos")

    endpoints = {
        "cables (geo)":         "https://www.submarinecablemap.com/api/v3/cable/cable-geo.json",
        "cables (lista)":       "https://www.submarinecablemap.com/api/v3/cable/all.json",
        "landing points (geo)": "https://www.submarinecablemap.com/api/v3/landing-point/landing-point-geo.json",
    }

    for nombre, url in endpoints.items():
        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                data = r.json()
                if isinstance(data, dict) and "features" in data:
                    print(f"  [OK] {nombre}: {len(data['features'])} features")
                elif isinstance(data, list):
                    print(f"  [OK] {nombre}: {len(data)} registros")
                else:
                    print(f"  [OK] {nombre}: respuesta recibida")
            else:
                print(f"  [ERROR] {nombre}: HTTP {r.status_code}")
        except Exception as e:
            print(f"  [FALLO] {nombre}: {e}")


# ─────────────────────────────────────────────
# 2. ACLED  (OAuth - email + password)
# ─────────────────────────────────────────────
def get_acled_token():
    """Solicita un Bearer token a ACLED via OAuth. Valido 24 horas."""
    r = requests.post(
        "https://acleddata.com/oauth/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "username":   ACLED_USERNAME,
            "password":   ACLED_PASSWORD,
            "grant_type": "password",
            "client_id":  "acled",
        },
        timeout=15,
    )
    if r.status_code == 200:
        return r.json().get("access_token")
    return None


def test_acled():
    separador("2. ACLED - Datos de conflicto armado")

    if "TU_NUEVA_PASSWORD" in ACLED_PASSWORD:
        print("  [SKIP] Credenciales no configuradas.")
        print("  Edita ACLED_PASSWORD en el script.")
        return

    print("  Solicitando token OAuth...")
    token = get_acled_token()

    if not token:
        print("  [ERROR] No se pudo obtener token. Verifica email y password.")
        return

    print(f"  [OK] Token obtenido: {token[:30]}...")

    # Prueba: ultimos 5 eventos en Iran
    r = requests.get(
        "https://acleddata.com/api/acled/read",
        headers={"Authorization": f"Bearer {token}"},
        params={
            "country": "Iran",
            "limit":   5,
            "fields":  "event_date|event_type|location|latitude|longitude|fatalities",
        },
        timeout=15,
    )

    if r.status_code == 200:
        data = r.json()
        eventos = data.get("data", [])
        print(f"  [OK] Eventos recibidos: {len(eventos)}")
        for e in eventos:
            print(
                f"       {e['event_date']} | {e['event_type']} | {e['location']}")
    else:
        print(f"  [ERROR] HTTP {r.status_code}: {r.text[:200]}")


# ─────────────────────────────────────────────
# 3. GLOBAL FISHING WATCH  (token Bearer)
# ─────────────────────────────────────────────
def test_gfw():
    separador("3. Global Fishing Watch - Trafico maritimo AIS")

    if "TU_TOKEN" in GFW_TOKEN:
        print("  [SKIP] Token no configurado.")
        print("  Registrate en: https://globalfishingwatch.org/our-apis/")
        return

    url = "https://gateway.api.globalfishingwatch.org/v3/4wings/report"
    headers = {
        "Authorization": f"Bearer {GFW_TOKEN}",
        "Content-Type":  "application/json",
    }
    payload = {
        "datasets": ["public-global-vessel-presence:latest"],
        "dateRange": {"start": "2024-01-01", "end": "2024-01-07"},
        "spatialResolution": "LOW",
        "temporalResolution": "YEARLY",
        "groupBy": "FLAG",
        "filters": [{}],
        "geometry": {
            "type": "Polygon",
            "coordinates": [[
                [55.8, 25.7], [57.2, 25.7],
                [57.2, 26.8], [55.8, 26.8],
                [55.8, 25.7],
            ]]
        }
    }

    try:
        r = requests.post(url, headers=headers, json=payload, timeout=20)
        if r.status_code == 200:
            data = r.json()
            print(f"  [OK] Respuesta recibida de GFW")
            print(f"       Claves en respuesta: {list(data.keys())}")
        elif r.status_code == 401:
            print("  [ERROR] 401 - Token invalido o expirado")
        else:
            print(f"  [ERROR] HTTP {r.status_code}: {r.text[:200]}")
    except Exception as e:
        print(f"  [FALLO] {e}")


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
if __name__ == "__main__":
    print("\nPRUEBAS DE CONEXION - Proyecto: Riesgo geopolitico cables submarinos")
    test_telegeography()
    test_acled()
    test_gfw()
    print("\n" + "=" * 55)
    print("  Pruebas completadas")
    print("=" * 55 + "\n")
