import requests
import re

def obtener_subcategorias(palabra, categoria):
    # Solicitud a la API de Wiktionary
    url = "https://fr.wiktionary.org/w/api.php"
    params = {
        "action": "query",
        "titles": palabra,
        "prop": "revisions",
        "rvprop": "content",
        "format": "json"
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    # Obtener el contenido de la página en formato wiki
    pages = data.get("query", {}).get("pages", {})
    page_content = ""
    for _, page in pages.items():
        if "revisions" in page:
            page_content = page["revisions"][0]["*"]
            break
    
    # Extraer la sección de francés usando un regex
    match_fr_section = re.search(r"==\s*\{\{langue\|fr\}\}\s*==(.+?)(?=\n==\s*\{\{langue\|)", page_content, re.DOTALL)
    if match_fr_section:
        fr_content = match_fr_section.group(1)
    else:
        return []  # Si no hay sección en francés, retornar lista vacía
    
    # Expresión regular para encontrar plantillas de categorías gramaticales complejas en la sección de francés
    sub_categorias = re.findall(r"=== \{\{S\|\s*" + re.escape(categoria) + r"\s*(\w*?)(?=\|fr\}\})", fr_content, re.IGNORECASE)
    
    # Eliminar duplicados si hay múltiples entradas de la misma categoría
    sub_categorias_unicas = list(set(sub_categorias))
    
    # Eliminar entradas vacías
    sub_categorias_unicas = [sub for sub in sub_categorias_unicas if sub]
    
    return sub_categorias_unicas