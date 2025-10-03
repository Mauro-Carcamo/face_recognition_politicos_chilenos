# 📌 Proyecto: Monitor de Políticos Chilenos en TV

---

## 📝 Bitácora del Proyecto (Resumen)

*   **Inicio:** Se planificó el proyecto para usar una base de datos relacional (primero SQLite, luego PostgreSQL) para almacenar los datos.
*   **Obstáculo:** Se encontraron problemas persistentes y bloqueantes de conexión a la base de datos PostgreSQL local, probablemente relacionados con la configuración del entorno del usuario (Firewall, etc.).
*   **Pivote Estratégico:** Para superar el bloqueo y avanzar, se tomó la decisión de **eliminar por completo la dependencia de bases de datos**. Se refactorizó el proyecto para usar un **archivo CSV (`parlamentarios.csv`)** como método de almacenamiento, simplificando enormemente la arquitectura.
*   **Hito Alcanzado:** Se completó con éxito la **Fase 1**, desarrollando un scraper funcional (`official_scraper.py`) que extrae los datos de todos los senadores y diputados desde `senado.cl` y `camara.cl` y los guarda en el CSV.
*   **Estado Actual:** En progreso la **Fase 2**, enfocada en la descarga y procesamiento de imágenes para el reconocimiento facial.

---

## 🎯 1. Objetivo General

Desarrollar un sistema automatizado que detecta, identifica y contabiliza el tiempo en pantalla de parlamentarios chilenos en transmisiones de televisión en vivo, utilizando Python y un enfoque basado en archivos para el almacenamiento de datos.

---

## 📂 2. Estructura de Carpetas del Proyecto

```
politicos-tv-monitor/
├─ data/
│  ├─ photos/                # Fotos descargadas, organizadas por parlamentario
│  │   ├─ senadores/
│  │   └─ diputados/
│  ├─ embeddings/              # Vectores de embeddings faciales
│  └─ parlamentarios.csv     # Archivo principal con los datos de los políticos
├─ src/
│  ├─ scraper/
│  │   ├─ official_scraper.py  # Script principal para senadores/diputados -> CSV
│  │   └─ photo_downloader.py  # Script para descargar ~10 fotos por persona
│  ├─ preprocessing/
│  │   └─ face_preprocessor.py
│  ├─ models/
│  │   └─ embedding_generator.py
│  └─ utils/
│      └─ logger.py
├─ reports/
└─ requirements.txt
```

---

## 🔧 3. Fases del Desarrollo

### ✅ Fase 1: Adquisición de Datos (Completada)

El objetivo de esta fase fue construir un archivo CSV consolidado con la información de cada parlamentario.

*   **Fuentes de Datos:** `senado.cl` y `camara.cl`.
*   **Proceso de Scraping:** El script `src/scraper/official_scraper.py` extrae nombre, partido, distrito/circunscripción y URL de perfil de ambas cámaras.
*   **Almacenamiento de Datos:** Toda la información se guarda en `data/parlamentarios.csv` con las siguientes columnas: `nombre_completo`, `partido`, `region`, `distrito_o_circunscripcion`, `camara`, `url_perfil`.

### ⏳ Fase 2: Descarga y Procesamiento de Fotos (En Progreso)

El objetivo es obtener un set de imágenes de alta calidad para cada político y prepararlas para el modelo de IA.

*   **Descarga de Múltiples Fotos (`src/scraper/photo_downloader.py`):**
    1.  El script lee `parlamentarios.csv`.
    2.  Para cada persona, realiza una búsqueda en Google Imágenes.
    3.  Descarga las primeras 10 imágenes relevantes.
    4.  Las guarda en una carpeta dedicada por persona (ej: `data/photos/senadores/nombre_del_senador/`).
*   **Preprocesamiento de Rostros (`src/preprocessing/face_preprocessor.py`):**
    1.  Para cada imagen descargada, se detectará el rostro con **RetinaFace**.
    2.  El rostro se alineará, recortará y normalizará (escala de grises, tamaño fijo).
*   **Generación de Embeddings (`src/models/embedding_generator.py`):**
    1.  Se usará un modelo **ArcFace** (`insightface`) para convertir cada rostro procesado en un vector numérico (embedding).
    2.  Estos embeddings se guardarán en la carpeta `data/embeddings/` para su uso en la fase de reconocimiento.

### ⬜ Fase 3: Monitoreo en Tiempo Real (Pendiente)

El núcleo del sistema: consumir streams de TV y realizar la detección.

*   **Ingesta de Streams:** Usar **Streamlink** y **FFmpeg** para capturar frames de video de canales chilenos.
*   **Worker de Detección:** Procesar frames en tiempo real, detectar rostros, generar embeddings y compararlos con nuestra base de datos de embeddings para encontrar coincidencias.

---

## 💻 4. Instalación y Dependencias

#### 4.1. Programas Externos

*   **Python:** 3.10 o superior.
*   **FFmpeg:** (Para la Fase 3).

#### 4.2. Librerías de Python (`requirements.txt`)

```
requests
beautifulsoup4
pandas
pillow
tqdm
# Para el reconocimiento facial
insightface
onnxruntime
numpy
# Para el procesamiento de video
opencv-python-headless
streamlink
```
