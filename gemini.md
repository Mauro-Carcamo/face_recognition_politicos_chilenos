# 📌 Proyecto: Monitor de Políticos Chilenos en TV

## 🎯 1. Objetivo General

Desarrollar un sistema automatizado que detecta, identifica y contabiliza el tiempo en pantalla de parlamentarios chilenos (diputados y senadores) en transmisiones de televisión en vivo. El proyecto se ejecutará localmente utilizando Python y herramientas de código abierto.

---

## 📂 2. Estructura de Carpetas del Proyecto

Se establece la siguiente estructura de directorios para mantener el proyecto organizado y escalable.

```
politicos-tv-monitor/
├─ data/
│  ├─ photos/
│  │   ├─ senadores/
│  │   └─ diputados/
│  ├─ embeddings/
│  │   ├─ senadores/
│  │   └─ diputados/
│  └─ metadata/
│      └─ parlamentarios.db
├─ src/
│  ├─ scraper/
│  │   └─ bcn_scraper.py
│  ├─ preprocessing/
│  │   └─ face_preprocessor.py
│  ├─ models/
│  │   └─ embedding_generator.py
│  ├─ realtime/
│  │   ├─ stream_handler.py
│  │   └─ detection_worker.py
│  └─ utils/
│      ├─ db_manager.py
│      └─ logger.py
├─ notebooks/
│  └─ 01_initial_exploration.ipynb
├─ reports/
│  └─ daily_appearance_report.csv
├─ requirements.txt
└─ gemini.yaml
```

---

## 🔧 3. Fases del Desarrollo

### Fase 1: Adquisición y Gestión de Datos

El objetivo de esta fase es construir una base de datos local y robusta con la información de cada parlamentario.

#### 3.1. Fuente de Datos

*   **Fuente Primaria:** [Biblioteca del Congreso Nacional (BCN) - Reseñas Parlamentarias](https://www.bcn.cl/portal/a-z/). Este portal centraliza la información de diputados y senadores y será nuestro objetivo principal de scraping.
*   **Fuentes Secundarias (Fallback):** `camara.cl` y `senado.cl`. Se usarán solo si la BCN no está disponible o la información está incompleta.

#### 3.2. Proceso de Scraping (`src/scraper/bcn_scraper.py`)

1.  **Navegación:** El scraper comenzará en la URL principal y seguirá los enlaces para cada parlamentario.
2.  **Extracción de Datos:** Por cada perfil, se extraerán los siguientes campos:
    *   `full_name`: Nombre completo.
    *   `party`: Partido político.
    *   `chamber`: "Diputado" o "Senador".
    *   `region`: Región que representa.
    *   `profile_url`: URL de la ficha en la BCN.
    *   `photo_url`: URL directa de la imagen de perfil.
3.  **Descarga de Imágenes:** Las fotos se descargarán en `data/photos/diputados` o `data/photos/senadores` y se nombrarán de forma estandarizada (ej: `apellido_nombre.jpg`).
4.  **Gestión de Errores y Logs:** Se implementará un sistema de reintentos con *exponential backoff* para errores de red (HTTP 429/5xx). Todas las acciones quedarán registradas.

#### 3.3. Base de Datos (`src/utils/db_manager.py`)

Se utilizará **SQLite** para la base de datos local (`parlamentarios.db`).

**Esquema de la Base de Datos:**

*   **`parlamentarios`**
    *   `id` (INTEGER, PK, AUTOINCREMENT)
    *   `person_id` (TEXT, UNIQUE): Identificador único (ej: `DIP_155` o `SEN_45`).
    *   `full_name` (TEXT)
    *   `party` (TEXT)
    *   `chamber` (TEXT)
    *   `region` (TEXT)
    *   `profile_url` (TEXT)
    *   `local_photo_path` (TEXT): Ruta a la foto en el disco.
    *   `photo_checksum` (TEXT): SHA256 de la imagen para detectar cambios.
    *   `created_at` (TIMESTAMP)
    *   `updated_at` (TIMESTAMP)

*   **`embeddings`**
    *   `id` (INTEGER, PK, AUTOINCREMENT)
    *   `person_id` (TEXT, FK a `parlamentarios.person_id`)
    *   `model_name` (TEXT): Ej: "ArcFace-iresnet50".
    *   `embedding_path` (TEXT): Ruta al archivo `.npy` del embedding.
    *   `generated_at` (TIMESTAMP)

*   **`apariciones`**
    *   `id` (INTEGER, PK, AUTOINCREMENT)
    *   `person_id` (TEXT, FK a `parlamentarios.person_id`)
    *   `channel_name` (TEXT)
    *   `start_timestamp` (TIMESTAMP)
    *   `duration_seconds` (INTEGER)
    *   `confidence_score` (REAL)

### Fase 2: Detección y Reconocimiento Facial

Esta fase se centra en procesar las imágenes para poder identificar a las personas.

#### 3.4. Preprocesamiento de Rostros (`src/preprocessing/face_preprocessor.py`)

1.  **Detección Facial:** Se utilizará **RetinaFace** (disponible en la librería `insightface`) para detectar el rostro en cada foto descargada. Es robusto ante variaciones de pose e iluminación.
2.  **Alineación y Recorte:** El rostro detectado será alineado (usando los puntos clave faciales) y recortado para normalizar la imagen.
3.  **Normalización:** La imagen se convertirá a escala de grises y se redimensionará al tamaño requerido por el modelo de embedding (ej: 112x112 pixels).

#### 3.5. Generación de Embeddings (`src/models/embedding_generator.py`)

1.  **Modelo de Embedding:** Se usará un modelo pre-entrenado de **ArcFace** (ej: `iresnet50`) a través de `insightface`. Estos modelos generan vectores (embeddings) de alta calidad que son muy efectivos para la comparación de rostros.
2.  **Generación y Almacenamiento:** Para cada parlamentario, se generará un vector de embedding a partir de su rostro preprocesado. El vector se guardará como un archivo `.npy` en la carpeta `data/embeddings/` y su ruta se registrará en la base de datos.

### Fase 3: Monitoreo en Tiempo Real

El núcleo del sistema: consumir streams de TV y realizar la detección.

#### 3.6. Ingesta de Streams (`src/realtime/stream_handler.py`)

1.  **Obtención de URL del Stream:** Se usará **Streamlink** para obtener la URL del stream HLS (`.m3u8`) de los canales de TV chilenos.
2.  **Captura de Frames:** Se utilizará **FFmpeg** (controlado desde Python con `subprocess`) para conectarse al stream y extraer frames a una tasa configurable (ej: 1 frame por segundo).

#### 3.7. Worker de Detección (`src/realtime/detection_worker.py`)

1.  **Procesamiento en Paralelo:** Se implementará un sistema productor-consumidor. El `stream_handler` (productor) pone frames en una cola, y uno o más `detection_worker` (consumidores) los procesan.
2.  **Detección y Reconocimiento por Frame:**
    *   Detectar todos los rostros en el frame con RetinaFace.
    *   Para cada rostro, generar un embedding en tiempo real.
    *   Comparar este embedding con los almacenados en `data/embeddings/` usando **similitud de coseno**.
    *   Si la similitud supera un umbral pre-calibrado (ej: 0.6), se considera una coincidencia.
3.  **Registro de Apariciones:** Cuando se identifica a un parlamentario, se registra un evento en la tabla `apariciones` de la base de datos, actualizando la duración si la persona sigue en pantalla en frames consecutivos.

---

## 💻 4. Instalación y Dependencias

#### 4.1. Programas Externos

*   **Python:** 3.11 o superior.
*   **FFmpeg:** Debe estar instalado y accesible en el PATH del sistema.

#### 4.2. Librerías de Python (`requirements.txt`)

```
requests
beautifulsoup4
pandas
sqlalchemy
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

---

## ⚡ 5. Flujo de Trabajo Sugerido

1.  **Semana 1:** Implementar el scraper (`bcn_scraper.py`) y el gestor de base de datos (`db_manager.py`). **Entregable:** Base de datos SQLite poblada con los datos de todos los parlamentarios y sus fotos descargadas.
2.  **Semana 2:** Desarrollar el pipeline de preprocesamiento y generación de embeddings. **Entregable:** Carpeta `data/embeddings` completa.
3.  **Semana 3:** Construir el prototipo de monitoreo en tiempo real para un solo canal. **Entregable:** Script que detecta y registra apariciones de un canal de TV.
4.  **Semana 4:** Refinar el sistema para manejar múltiples canales, mejorar el registro y generar reportes básicos. **Entregable:** Versión funcional del monitor y un dashboard simple.