import requests
import re
from tqdm import tqdm
from requests.exceptions import Timeout, RequestException
import time

def load_words(url, category):
    results = []
    continue_fetching = True
    query_url = url
    regex = re.compile(r"^[A-Za-zÀ-ÿ]+$")  # Solo palabras con letras (incluyendo letras acentuadas)
    progress_bar = tqdm(desc="Descargando", unit=" páginas consultadas")  # Configura la barra de progreso

    # Crea una sesión para reutilizar la conexión
    session = requests.Session()

    while continue_fetching:
        try:
            response = session.get(query_url, timeout=30)  # Timeout de 30 segundos
            response.raise_for_status()  # Lanza una excepción para códigos de error HTTP
            data = response.json()

            filtered_results = [
                member['title'] for member in data['query']['categorymembers']
                if regex.match(member['title'])
            ]

            results.extend(filtered_results)
            progress_bar.update(1)
            progress_bar.set_postfix({"category": category, "words": len(results)})

            continue_exists = data.get('continue', None)
            continue_value = continue_exists.get('cmcontinue', None) if continue_exists else None
            if continue_value:
                query_url = f"{url}&cmcontinue={continue_value}"
            else:
                continue_fetching = False
                break # Rompe el bucle cuando no hay más páginas para descargar

        except Timeout:
            print("Timeout alcanzado, intentando de nuevo...")
            time.sleep(2)  # Esperar 2 segundos antes de reintentar
        except RequestException as e:
            print(f"Error en la solicitud: {e}")
            break  # Rompe el bucle en caso de error crítico

    progress_bar.set_postfix()  # Limpia los datos de la barra de progreso
    progress_bar.close()  # Cierra la barra de progreso cuando se complete la descarga

    # Cierra la sesión
    session.close()

    return results
