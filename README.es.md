# Hormuz Cable Risk
### Índice de Riesgo Geopolítico para la Infraestructura de Cables Submarinos en el Estrecho de Ormuz

---

## Descripción

Este proyecto construye un **índice de vulnerabilidad digital** para los países cuya infraestructura de cables submarinos atraviesa el Estrecho de Ormuz, uno de los puntos de estrangulamiento más estratégicos y geopolíticamente volátiles del mundo.

Cruzando tres fuentes de datos independientes, el proyecto identifica qué países están más expuestos al aislamiento digital en caso de daño a los cables, ya sea accidental o deliberado.

---

## La Pregunta que Responde este Proyecto

> *Si los cables submarinos en el Estrecho de Ormuz son dañados, ¿qué países pierden más conectividad y qué tan vulnerables son?*

---

## Fuentes de Datos

| Fuente | Descripción | Acceso |
|--------|-------------|--------|
| [TeleGeography Submarine Cable Map](https://www.submarinecablemap.com) | Rutas de cables, puntos de aterrizaje, propietarios, fechas de servicio | API pública |
| [UCDP Georeferenced Event Dataset](https://ucdp.uu.se/downloads) | Eventos de conflicto armado con coordenadas, 1989–2026 | Descarga gratuita |
| [UCDP Candidate Dataset](https://ucdp.uu.se/downloads) | Eventos de conflicto preliminares, publicación mensual | Descarga gratuita |
| [AISstream](https://aisstream.io) | Tráfico marítimo AIS en tiempo real vía WebSocket | API gratuita |

---

## Metodología

El **Índice de Vulnerabilidad Digital** se calcula por país usando cuatro componentes:

| Componente | Peso | Descripción |
|------------|------|-------------|
| Exposición | 35% | Eventos de conflicto UCDP dentro de 50km de los puntos de aterrizaje (2020–2026) |
| Dependencia | 30% | Porcentaje de cables del país que pasan por la zona de riesgo del Golfo |
| Redundancia | 20% | Número total de cables que sirven al país (inverso) |
| Concentración | 15% | Máximo de cables compartiendo un solo punto de aterrizaje |

Cada componente se normaliza a [0, 1] antes de aplicar los pesos.

---

## Resultados

| País | Cables Totales | Cables en Zona | Eventos Conflicto | Índice de Riesgo |
|------|---------------|----------------|-------------------|-----------------|
| Yemen | 5 | 5 | 569 | **0.652** |
| Pakistan | 9 | 9 | 306 | **0.487** |
| Iraq | 4 | 4 | 0 | 0.396 |
| Kuwait | 6 | 6 | 6 | 0.342 |
| Arabia Saudita | 24 | 24 | 0 | 0.312 |
| Emiratos Árabes Unidos | 21 | 21 | 8 | 0.283 |
| Irán | 6 | 6 | 13 | 0.278 |
| Qatar | 9 | 9 | 8 | 0.262 |
| Bahréin | 7 | 7 | 0 | 0.261 |
| Omán | 20 | 20 | 0 | **0.226** |

**Hallazgo principal:** Yemen y Pakistan muestran la mayor vulnerabilidad debido a la baja redundancia de cables combinada con actividad de conflicto significativa cerca de su infraestructura costera. Omán, a pesar de ser el país geográficamente más cercano al Estrecho, obtiene el índice más bajo gracias a su alta redundancia de cables y ausencia de conflicto cercano.

**Nota sobre Irán:** El índice probablemente subestima el riesgo real de Irán. UCDP captura eventos de conflicto armado verificados, no operaciones navales, interrupciones relacionadas con sanciones ni presión geopolítica, factores que en la práctica afectan significativamente la conectividad iraní.

---

## Outputs

- **`outputs/mapa_completo.html`** - Mapa interactivo combinado con rutas de cables, heatmap de conflicto, puntos de aterrizaje e índice de riesgo por país
- **`outputs/mapa_riesgo.html`** - Mapa interactivo simplificado de riesgo
- **`data/processed/indice_riesgo.csv`** - Tabla completa del índice con todos los componentes

---

## Estructura del Proyecto

```
hormuz-cable-risk/
├── README.md
├── README.es.md
├── requirements.txt
├── .gitignore
├── data/
│   ├── raw/               # Archivos de datos crudos (no rastreados en Git)
│   └── processed/         # Datasets limpios y procesados
│       ├── cables.csv
│       ├── landing_points.csv
│       ├── landing_points_coords.csv
│       ├── ucdp_gulf_zone.csv
│       └── indice_riesgo.csv
├── src/
│   ├── construir_dataset.py       # Pipeline de datos TeleGeography
│   ├── combinar_ucdp.py           # Combina 4 archivos CSV de UCDP
│   ├── explorar_telegeography.py  # Exploración de TeleGeography
│   ├── explorar_ucdp.py           # Exploración de UCDP
│   ├── indice_riesgo.py           # Cálculo del índice de riesgo
│   ├── mapa_riesgo.py             # Mapa de riesgo simplificado
│   ├── mapa_completo.py           # Mapa interactivo combinado
│   └── capturar_ais.py            # Captura de tráfico AIS en tiempo real
└── outputs/                       # Mapas generados (no rastreados en Git)
```

---

## Cómo Reproducir

```bash
# 1. Clonar el repositorio
git clone https://github.com/CarolinaMCruz/hormuz-cable-risk.git
cd hormuz-cable-risk

# 2. Crear y activar el entorno virtual
python -m venv venv
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Descargar datasets de UCDP manualmente
# Ir a: https://ucdp.uu.se/downloads
# Descargar: GED Global v25.1, Candidate v25.01.25.12, v26.0.1, v26.0.2
# Colocar todos los archivos CSV en: data/raw/

# 5. Ejecutar el pipeline
python src/construir_dataset.py     # Construir dataset de TeleGeography
python src/combinar_ucdp.py         # Combinar datasets UCDP
python src/indice_riesgo.py         # Calcular índice de riesgo
python src/mapa_completo.py         # Generar mapa interactivo

# 6. Abrir el mapa
open outputs/mapa_completo.html

# 7. (Opcional) Capturar tráfico AIS en tiempo real
# Requiere API key gratuita de aisstream.io
python src/capturar_ais.py --minutos 5
```

---

## Limitaciones

- Los datos de UCDP cubren eventos de conflicto armado verificados. Las operaciones navales, ataques cibernéticos y tensiones geopolíticas no están capturados, lo que probablemente subestima el riesgo de Irán y el contexto más amplio del conflicto EEUU-Israel-Irán.
- Los datos de presencia de embarcaciones de Global Fishing Watch (AIS) no fueron integrados por restricciones de acceso. Agregar la densidad de embarcaciones cerca de las rutas de cables mejoraría significativamente el componente de exposición.
- Las geometrías de rutas de cables de TeleGeography son representaciones cartográficas, no datos de ingeniería precisos.
- El índice aplica tratamiento geográfico uniforme a todos los eventos de conflicto dentro del radio, independientemente de si afectan específicamente la infraestructura marítima.

---

## Stack Tecnológico

- Python 3.12
- pandas, geopandas, shapely
- folium
- requests, websockets

---

*Cobertura de datos: 1989 - febrero 2026*
