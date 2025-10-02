# Monitor de Políticos Chilenos en TV (face_recognition_politicos_chilenos)

Este proyecto es un sistema automatizado para detectar, identificar y contabilizar el tiempo en pantalla de parlamentarios chilenos (diputados y senadores) en transmisiones de televisión en vivo.

## 🎯 Objetivo

El objetivo principal es generar métricas objetivas sobre la presencia mediática de los políticos en los principales canales de televisión de Chile, proveyendo datos para análisis periodístico, académico o de interés público.

## ✨ Características

- **Scraping Automatizado:** Recolecta automáticamente fotos y datos de parlamentarios desde fuentes oficiales como la Biblioteca del Congreso Nacional de Chile (BCN).
- **Reconocimiento Facial:** Utiliza modelos de Deep Learning (RetinaFace para detección y ArcFace for embedding) para identificar rostros con alta precisión.
- **Monitoreo en Tiempo Real:** Capaz de procesar streams de video en vivo, detectar apariciones de políticos y registrar la duración.
- **Base de Datos Local:** Almacena toda la información en una base de datos SQLite para fácil consulta y análisis.
- **Reportes:** Genera reportes con las métricas de tiempo en pantalla.

## 🛠️ Stack Tecnológico

- **Lenguaje:** Python 3.11+
- **Scraping:** `requests`, `BeautifulSoup4`
- **Reconocimiento Facial:** `insightface`, `onnxruntime`, `numpy`
- **Procesamiento de Video:** `opencv-python`, `streamlink`, `ffmpeg`
- **Base de Datos:** `SQLite`

## 🚀 Cómo Empezar

### Prerrequisitos

- Python 3.11 o superior.
- FFmpeg instalado y accesible en el PATH del sistema.

### Instalación

1.  **Clonar el repositorio (reemplaza la URL con la tuya):**
    ```bash
    git clone https://github.com/tu-usuario/face_recognition_politicos_chilenos.git
    cd face_recognition_politicos_chilenos
    ```

2.  **Crear un entorno virtual e instalar dependencias:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # En Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```

3.  **Inicializar la base de datos:**
    ```bash
    python src/utils/db_manager.py
    ```

4.  **Ejecutar el scraper para poblar la base de datos:**
    ```bash
    python src/scraper/bcn_scraper.py
    ```

## Fases del Proyecto

1.  **Fase 1: Adquisición de Datos:** Scraping de datos y fotos de parlamentarios.
2.  **Fase 2: Reconocimiento Facial:** Preprocesamiento de imágenes y generación de embeddings.
3.  **Fase 3: Monitoreo en Tiempo Real:** Detección en streams de video.
4.  **Fase 4: Análisis y Visualización:** Creación de reportes y dashboards.
