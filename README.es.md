# Riesgo de Cables en Ormuz
### Índice de Vulnerabilidad para la Infraestructura de Cables Costeros en la Zona del Golfo

---

## Resumen

Este proyecto construye un **índice de vulnerabilidad de infraestructura costera** para los países cuyos puntos de amarre de cables submarinos se encuentran en la zona del Golfo — los puntos de entrada y salida costeros donde los cables están más expuestos a daños.

Los puntos de amarre representan el segmento más vulnerable de cualquier sistema de cables submarinos: son accesibles, están concentrados y rodeados de infraestructura de apoyo que puede verse interrumpida por conflictos o inestabilidad cercana.

---

## La pregunta que responde este proyecto

> *¿Qué países de la zona del Golfo tienen la infraestructura de amarre de cables más expuesta y cómo aumenta su vulnerabilidad el conflicto cercano?*

---

## Fuentes de Datos

| Fuente | Descripción | Acceso |
|--------|-------------|--------|
| [TeleGeography Submarine Cable Map](https://www.submarinecablemap.com) | Rutas de cables, puntos de amarre, propietarios, fechas RFS | API Pública |
| [UCDP Georeferenced Event Dataset](https://ucdp.uu.se/downloads) | Eventos de conflictos armados con coordenadas, 1989–2026 | Descarga gratuita |
| [UCDP Candidate Dataset](https://ucdp.uu.se/downloads) | Eventos de conflicto preliminares, publicación mensual | Descarga gratuita |

---

## Metodología

El **Índice de Vulnerabilidad Digital** se calcula por país utilizando cuatro componentes:

| Componente | Peso | Descripción |
|------------|------|-------------|
| Exposición | 35% | Eventos de conflicto UCDP a menos de 50 km de los puntos de amarre (2020–2026) |
| Dependencia | 30% | Proporción de los cables de un país que pasan por la zona de riesgo del Golfo |
| Redundancia | 20% | Número total de cables que dan servicio al país (inverso) |
| Concentración| 15% | Número máximo de cables que comparten un mismo punto de amarre |

Cada componente se normaliza de [0, 1] antes de aplicar el peso.

---

## Resultados

| País | Total de Cables | Cables en Zona | Eventos de Conflicto | Índice de Riesgo |
|---------|-------------|----------------|-----------------|------------|
| Yemen | 5 | 5 | 569 | **0.652** |
| Pakistán | 9 | 9 | 306 | **0.487** |
| Irak | 4 | 4 | 0 | 0.396 |
| Kuwait | 6 | 6 | 6 | 0.342 |
| Arabia Saudita | 24 | 24 | 0 | 0.312 |
| EAU | 21 | 21 | 8 | 0.283 |
| Irán | 6 | 6 | 13 | 0.278 |
| Qatar | 9 | 9 | 8 | 0.262 |
| Baréin | 7 | 7 | 0 | 0.261 |
| Omán | 20 | 20 | 0 | **0.226** |

**Hallazgo clave:** Yemen y Pakistán muestran la mayor vulnerabilidad debido a la baja redundancia de cables combinada con una actividad de conflicto significativa cerca de su infraestructura costera. Omán, a pesar de ser geográficamente el más cercano al Estrecho, obtiene la puntuación más baja debido a su alta redundancia de cables y la ausencia de conflictos cercanos.

**Nota sobre Irán:** Es probable que el índice subestime el riesgo real de Irán. UCDP captura eventos de conflicto armado verificados, no operaciones navales, interrupciones relacionadas con sanciones o presión geopolítica, factores que afectan significativamente su conectividad en la práctica.

---

## Entregables (Outputs)

- **`outputs/mapa_completo.html`** — Mapa interactivo que combina rutas de cables, mapa de calor de conflictos, puntos de amarre e índice de riesgo por país.
- **`outputs/mapa_riesgo.html`** — Mapa de riesgo interactivo simplificado.
- **`data/processed/indice_riesgo.csv`** — Tabla completa del índice con todos sus componentes.

---

## Estructura del Proyecto

```
hormuz-cable-risk/
├── README.md
├── requirements.txt
├── .gitignore
├── data/
│   ├── raw/               # Archivos de datos brutos (no rastreados en Git)
│   └── processed/         # Conjuntos de datos limpios y procesados
│       ├── cables.csv
│       ├── landing_points.csv
│       ├── landing_points_coords.csv
│       ├── ucdp_gulf_zone.csv
│       └── indice_riesgo.csv
├── src/
│   ├── construir_dataset.py       # Pipeline de datos de TeleGeography
│   ├── combinar_ucdp.py           # Combina los 4 archivos CSV de UCDP
│   ├── explorar_telegeography.py  # Exploración de TeleGeography
│   ├── explorar_ucdp.py           # Exploración de UCDP
│   ├── indice_riesgo.py           # Cálculo del índice de riesgo
│   ├── mapa_riesgo.py             # Mapa de riesgo simple
│   └── mapa_completo.py           # Mapa interactivo combinado
└── outputs/                       # Mapas generados (no rastreados en Git)
```

---

## Cómo reproducirlo

```bash
# 1. Clonar el repositorio
git clone https://github.com/CarolinaMCruz/hormuz-cable-risk.git
cd hormuz-cable-risk

# 2. Crear y activar el entorno virtual
python -m venv venv
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Descargar los datasets de UCDP manualmente
# Ir a: https://ucdp.uu.se/downloads
# Descargar: GED Global v25.1, Candidate v25.01.25.12, v26.0.1, v26.0.2
# Colocar todos los archivos CSV en: data/raw/

# 5. Ejecutar el pipeline
python src/construir_dataset.py     # Construir dataset de TeleGeography
python src/combinar_ucdp.py         # Combinar datasets de UCDP
python src/indice_riesgo.py         # Calcular índice de riesgo
python src/mapa_completo.py         # Generar mapa interactivo

# 6. Abrir el mapa
open outputs/mapa_completo.html
```

---

## Limitaciones

- Los datos de UCDP cubren eventos de conflicto armado verificados. No se capturan operaciones navales, ciberataques ni tensiones geopolíticas, lo que probablemente subestima el riesgo para Irán y el contexto general del conflicto EE. UU.-Israel-Irán.
- No se integraron los datos de presencia de buques (AIS) de Global Fishing Watch debido a restricciones de acceso. Añadir la densidad de buques cerca de las rutas de los cables mejoraría significativamente el componente de exposición.
- Las geometrías de las rutas de los cables de TeleGeography son representaciones cartográficas, no datos de ingeniería precisos.
- El índice aplica el mismo tratamiento geográfico a todos los eventos de conflicto dentro del radio, independientemente de si se dirigen específicamente a la infraestructura marítima.
- Se probó el rastreo de buques en tiempo real de AISstream, pero el servicio no estaba disponible en el momento del desarrollo. El script de captura (`src/capturar_ais.py`) se incluye para uso futuro cuando se restablezca el servicio.
- Este índice mide el riesgo en los puntos de amarre (infraestructura costera), no a lo largo de las rutas de los cables submarinos en el lecho marino. El riesgo en el fondo marino por el anclaje de buques o la pesca requiere datos de tráfico de buques AIS, que no estuvieron disponibles para este proyecto.

---

## Tecnologías Utilizadas

- Python 3.12
- pandas, geopandas, shapely
- folium
- requests

---

*Cobertura de datos: 1989 – Febrero 2026*