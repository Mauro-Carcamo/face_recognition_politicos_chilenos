import csv
import requests
from bs4 import BeautifulSoup
from pathlib import Path

def scrape_senado(csv_writer):
    """Función para scrapear los datos del Senado y escribirlos en un CSV."""
    URL = "https://www.senado.cl/senadoras-y-senadores/listado-de-senadoras-y-senadores"
    print(f"Scrapeando Senado desde: {URL}")
    
    try:
        response = requests.get(URL)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        senators_found = 0
        name_headings = soup.find_all('h3')

        for name_h3 in name_headings:
            card = name_h3.find_parent('a')
            if not card:
                continue

            full_name = name_h3.text.strip()
            
            profile_url = card.get('href', '')
            if profile_url and not profile_url.startswith('http'):
                profile_url = f"https://www.senado.cl{profile_url}"

            details_list = card.find('ul')
            if not details_list:
                continue
                
            list_items = details_list.find_all('li')
            if len(list_items) < 2:
                continue

            constituency = list_items[0].find('h4').text.strip()
            region = list_items[0].find('p').text.strip()
            party = list_items[1].find('h4').text.strip()
            
            # Escribir la fila en el archivo CSV
            csv_writer.writerow([full_name, party, region, constituency, 'Senador', profile_url])
            
            senators_found += 1
            print(f"Procesado: {full_name}")

        print(f"Se procesaron y guardaron {senators_found} senadores.")

    except requests.exceptions.RequestException as e:
        print(f"Error de red al scrapear el Senado: {e}")
    except Exception as e:
        print(f"Ocurrió un error inesperado en scrape_senado: {e}")

def scrape_camara(csv_writer):
    """Función para scrapear los datos de la Cámara de Diputados y escribirlos en un CSV."""
    URL = "https://www.camara.cl/diputados/diputados.aspx"
    print(f"Scrapeando Cámara de Diputados desde: {URL}")
    
    try:
        response = requests.get(URL)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        deputies_found = 0
        
        # Estrategia más simple: buscar todas las etiquetas <article>
        articles = soup.find_all('article')
        
        if not articles:
            print("No se encontró ninguna etiqueta <article>. La estructura puede haber cambiado.")
            return

        for article in articles:
            name_element = article.find('h4')
            if not name_element:
                continue # No es una tarjeta de diputado válida

            # Asegurarse de que es una tarjeta de diputado (p.ej. que tiene un partido)
            details = article.find_all('p')
            if len(details) < 2 or 'Partido:' not in details[1].text:
                continue # Omitir artículos que no son de diputados (como la mesa directiva o exdiputados)

            full_name = name_element.text.strip()
            
            profile_link = article.find('a')
            profile_url = profile_link['href'] if profile_link else ''
            if profile_url and not profile_url.startswith('http'):
                profile_url = f"https://www.camara.cl{profile_url}"

            district = details[0].text.replace('Distrito:', '').strip()
            party = details[1].text.replace('Partido:', '').strip()
            region = '' # La región no está disponible en esta vista

            csv_writer.writerow([full_name, party, region, district, 'Diputado', profile_url])
            
            deputies_found += 1
            print(f"Procesado: {full_name}")

        print(f"Se procesaron y guardaron {deputies_found} diputados.")

    except requests.exceptions.RequestException as e:
        print(f"Error de red al scrapear la Cámara: {e}")
    except Exception as e:
        print(f"Ocurrió un error inesperado en scrape_camara: {e}")

def main():
    """Función principal que orquesta el scraping y guarda en CSV."""
    print("--- Iniciando scraper para guardar en CSV ---")
    
    # Definir el path del archivo de salida
    output_file = Path("data") / "parlamentarios.csv"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            
            # Escribir la fila de encabezado
            header = ['nombre_completo', 'partido', 'region', 'distrito_o_circunscripcion', 'camara', 'url_perfil']
            csv_writer.writerow(header)
            
            # Ejecutar el scraping para cada cámara, pasando el writer
            scrape_senado(csv_writer)
            scrape_camara(csv_writer)
            
    except IOError as e:
        print(f"Error escribiendo el archivo CSV: {e}")
            
    print(f"--- Proceso de Scraping Finalizado. Datos guardados en {output_file} ---")

if __name__ == "__main__":
    main()