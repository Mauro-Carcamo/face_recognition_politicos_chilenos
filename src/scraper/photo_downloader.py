import pandas as pd
import os
from pathlib import Path
import time
import base64
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# --- Constantes ---
CSV_FILE = Path("data") / "parlamentarios.csv"
PHOTOS_DIR = Path("data") / "photos"

def download_images_for_person(driver, name, chamber):
    """Busca y descarga ~10 imágenes para una persona específica usando Selenium."""
    print(f"--- Buscando imágenes para: {name} ({chamber}) ---")
    
    safe_folder_name = "".join(c for c in name if c.isalnum() or c in (' ', '_')).rstrip().replace(' ', '_').lower()
    person_dir = PHOTOS_DIR / chamber.lower() / safe_folder_name
    person_dir.mkdir(parents=True, exist_ok=True)

    query = f'fotos {chamber} {name}'
    print(f"Consulta de búsqueda: {query}")

    try:
        driver.get("https://images.google.com")
        time.sleep(random.uniform(1, 2.5))

        search_box = driver.find_element(By.NAME, "q")
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)
        time.sleep(random.uniform(2, 3.5))

        # Simular scroll para cargar más imágenes
        print("Haciendo scroll para cargar imágenes...")
        for _ in range(2):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(1, 2))

        print("Extrayendo URLs de imágenes...")
        all_images = driver.find_elements(By.TAG_NAME, "img")
        image_urls = []
        for img in all_images:
            src = img.get_attribute('src')
            if src and src.startswith('data:image/jpeg;base64,'):
                image_urls.append(src)
        image_urls = image_urls[:15]

        if not image_urls:
            print("No se encontraron imágenes con el formato esperado (base64).")
            return

        download_count = 0
        for i, url in enumerate(image_urls):
            if download_count >= 10:
                break
            try:
                header, encoded = url.split(',', 1)
                img_data = base64.b64decode(encoded)
                
                file_path = person_dir / f"{download_count + 1}.jpg"
                with open(file_path, 'wb') as f:
                    f.write(img_data)
                print(f"Guardada imagen {download_count + 1}.jpg")
                download_count += 1

            except Exception as e:
                print(f"No se pudo procesar o guardar la imagen {i+1}. Error: {e}")

        print(f"Se descargaron {download_count} imágenes para {name}.")

    except Exception as e:
        print(f"Ocurrió un error durante la automatización del navegador: {e}")

def main():
    """Función principal que orquesta la descarga de fotos para los políticos faltantes."""
    
    missing_politicians = [
        ("Sr. Christian Matheson", "Diputado"),
        ("Sr. Cristóbal Martínez", "Diputado"),
        ("Sr. Francisco Pulgar", "Diputado"),
        ("Sr. Francisco Undurraga", "Diputado"),
        ("Sr. Guillermo Ramírez", "Diputado"),
        ("Sr. Jaime Naranjo", "Diputado"),
        ("Sr. Jorge Rathgeb", "Diputado"),
        ("Sr. José Carlos Meza", "Diputado"),
        ("Sr. Mauricio Ojeda", "Diputado"),
        ("Sra. Camila Musante", "Diputado"),
        ("Sra. Carolina Marzán", "Diputado"),
        ("Sra. Gael Yeomans", "Diputado"),
        ("Sra. Marcia Raphael", "Diputado"),
        ("Sra. Marisela Santibáñez", "Diputado")
    ]

    print(f"--- Iniciando descarga para los {len(missing_politicians)} políticos faltantes ---")

    # Configurar Selenium
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    try:
        for name, chamber in missing_politicians:
            download_images_for_person(driver, name, chamber)
            print("-" * 20)
            time.sleep(random.uniform(2, 5))
    finally:
        if driver:
            driver.quit()
        print("Navegador cerrado.")

if __name__ == "__main__":
    main()