import requests
from bs4 import BeautifulSoup
import pandas as pd
from pathlib import Path
import time
import hashlib
import sqlite3

# Importar nuestros módulos locales
import sys
# Añadir el directorio src al path para poder importar utils
sys.path.append(str(Path(__file__).resolve().parent.parent))
from utils.logger import get_logger
from utils.db_manager import create_connection, DB_FILE

# --- Constantes ---
BASE_URL = "https://www.bcn.cl"
START_URL = f"{BASE_URL}/portal/a-z/"

# Simular un navegador para evitar bloqueos
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

PHOTO_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "photos"
LOG = get_logger("bcn_scraper")


def get_parliamentarian_links():
    """Obtiene las URLs de los perfiles de todos los parlamentarios desde la página A-Z."""
    links = []
    try:
        response = requests.get(START_URL, headers=HEADERS)
        response.raise_for_status() # Lanza un error para códigos 4xx/5xx
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Encontrar la sección de listado
        list_section = soup.find('div', class_='container-fluid')
        if not list_section:
            LOG.error("No se encontró la sección principal del listado de parlamentarios.")
            return []

        # Extraer todos los enlaces que apuntan a un perfil
        for a_tag in list_section.find_all('a', href=True):
            if "/portal/a-z/" in a_tag['href'] and a_tag['href'] != "/portal/a-z/":
                full_link = f"{BASE_URL}{a_tag['href']}"
                if full_link not in links:
                    links.append(full_link)
        
        LOG.info(f"Se encontraron {len(links)} links a perfiles de parlamentarios.")
        return links

    except requests.exceptions.RequestException as e:
        LOG.error(f"Error al acceder a la página principal {START_URL}: {e}")
        return []

def scrape_profile(profile_url, conn):
    """Extrae la información de un perfil individual, descarga la foto y la guarda en la DB."""
    try:
        LOG.info(f"Procesando perfil: {profile_url}")
        response = requests.get(profile_url, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # --- Extracción de datos ---
        # El nombre suele estar en un h1 con una clase específica
        full_name = soup.find('h1', class_='ficha_nombre').text.strip()
        
        # La foto está en un img con una clase específica
        photo_relative_url = soup.find('img', class_='ficha_foto')['src']
        photo_url = f"{BASE_URL}{photo_relative_url}"

        # Los demás datos suelen estar en una lista de definiciones (dl)
        details = {}
        for dl in soup.find_all('dl'):
            for dt, dd in zip(dl.find_all('dt'), dl.find_all('dd')):
                details[dt.text.strip()] = dd.text.strip()

        party = details.get('Partido', 'No especificado')
        chamber = 'Senador' if 'Senado' in details.get('Tipo de Parlamentario', '') else 'Diputado'
        region = details.get('Región', 'No especificada')

        # --- Procesamiento de la imagen ---
        photo_response = requests.get(photo_url, headers=HEADERS)
        photo_response.raise_for_status()
        photo_bytes = photo_response.content
        photo_checksum = hashlib.sha256(photo_bytes).hexdigest()

        # Guardar la foto
        chamber_dir = 'senadores' if chamber == 'Senador' else 'diputados'
        PHOTO_DIR.joinpath(chamber_dir).mkdir(parents=True, exist_ok=True)
        # Limpiar el nombre para usarlo como nombre de archivo
        safe_filename = "".join(c for c in full_name if c.isalnum() or c in (' ', '_')).rstrip()
        safe_filename = safe_filename.replace(' ', '_').lower() + ".jpg"
        local_photo_path = PHOTO_DIR / chamber_dir / safe_filename
        
        with open(local_photo_path, 'wb') as f:
            f.write(photo_bytes)

        # --- Preparar datos para la DB ---
        # Generar un ID único a partir de la URL
        person_id = f"{chamber.upper()[:3]}_{profile_url.strip('/').split('/')[-1]}"

        data = {
            'person_id': person_id,
            'full_name': full_name,
            'party': party,
            'chamber': chamber,
            'region': region,
            'profile_url': profile_url,
            'local_photo_path': local_photo_path,
            'photo_checksum': photo_checksum
        }

        # --- Insertar o Actualizar en DB ---
        from utils.db_manager import insert_or_update_parlamentario
        status = insert_or_update_parlamentario(conn, data)
        LOG.info(f"Resultado para {full_name}: {status}")

        time.sleep(0.5) # Ser respetuosos con el servidor

    except requests.exceptions.RequestException as e:
        LOG.error(f"Error de red procesando {profile_url}: {e}")
    except (AttributeError, KeyError) as e:
        LOG.error(f"Error de parsing en {profile_url}. Es posible que la estructura HTML haya cambiado. Error: {e}")
    except Exception as e:
        LOG.error(f"Ocurrió un error inesperado procesando {profile_url}: {e}")


def main():
    """Función principal para orquestar el proceso de scraping."""
    LOG.info("--- Iniciando Proceso de Scraping ---")
    
    # Obtener links de perfiles
    profile_links = get_parliamentarian_links()

    if not profile_links:
        LOG.error("No se pudieron obtener los links de los perfiles. Abortando.")
        return

    # Conexión a la base de datos
    conn = create_connection()
    if not conn:
        LOG.error("No se pudo establecer conexión con la base de datos. Abortando.")
        return

    # Procesar cada perfil
    for link in profile_links:
        scrape_profile(link, conn)

    conn.close()
    LOG.info("--- Proceso de Scraping Finalizado ---")

if __name__ == '__main__':
    main()
