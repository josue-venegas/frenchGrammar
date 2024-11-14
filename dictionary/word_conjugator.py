import requests
from bs4 import BeautifulSoup

def obtener_persona(persona):
    personas = {
        '1s': {'j’', 'je', 'j’ai', 'j’avais', 'j’eus', 'j’aurai', 'que j’', 'que je', 'que j’aie', 'que j’eusse', 'j’aurais', 
               'je m’', 'je me', 'je me suis', 'je m’étais', 'je me fus', 'je me serai', 'que je m’', 'que je me sois', 'que je me fusse', 'je me serais'},
        '2s': {'t’','tu', 'tu as', 'tu avais', 'tu eus', 'tu auras', 'que t’', 'que tu', 'que tu aies', 'que tu eusses', 'tu aurais',
               'tu t’', 'tu te', 'tu t’es', 'tu t’étais', 'tu te fus', 'tu te seras', 'que tu t’', 'que tu te sois', 'que tu te fusses', 'tu te serais',
               },
        '3s': {'il/elle/on', 'il/elle/on a', 'il/elle/on avait', 'il/elle/on eut', 'il/elle/on aura', 
               'qu’il/elle/on', 'qu’il/elle/on ait', 'qu’il/elle/on eût', 'il/elle/on aurait', 'qu’il/elle/on s’', 'qu’il/elle/on se', 'qu’il/elle/on se fût', 'qu’il/elle/on se soit', 'il/elle/on se serait',
               'il/elle/on s’', 'il/elle/on se', 'il/elle/on s’est', 'il/elle/on s’était', 'il/elle/on se fut', 'il/elle/on se sera',},
        '1p': {'nous', 'nous avons', 'nous avions', 'nous eûmes', 'nous aurons', 'que nous', 'que nous ayons', 'que nous eussions', 'nous aurions',
               'nous nous', 'nous nous sommes', 'nous nous étions', 'nous nous fûmes', 'nous nous serons', 'que nous nous', 'que nous nous soyons', 'que nous nous fussions', 'nous nous serions',
               },
        '2p': {'vous', 'vous avez', 'vous aviez', 'vous eûtes', 'vous aurez', 'que vous', 'que vous ayez', 'que vous eussiez', 'vous auriez',
               'vous vous', 'vous vous êtes', 'vous vous étiez', 'vous vous fûtes', 'vous vous serez', 'que vous vous', 'que vous vous soyez', 'que vous vous fussiez', 'vous vous seriez',
               },
        '3p': {'ils/elles', 'ils/elles ont', 'ils/elles avaient', 'ils/elles eurent', 'ils/elles auront', 'qu’ils/elles', 'qu’ils/elles aient', 'qu’ils/elles eussent', 'ils/elles auraient',
               'ils/elles s’', 'ils/elles se', 'ils/elles se sont', 'ils/elles s’étaient', 'ils/elles se furent', 'ils/elles se seront', 'qu’ils/elles s’', 'qu’ils/elles se', 'qu’ils/elles se soient', 'qu’ils/elles se fussent', 'ils/elles se seraient'}
    }
    
    for key, valores in personas.items():
        if persona in valores:
            return key
    return None

def descargar_html(url):
    # Descargar el contenido HTML de la página
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Encontrar el contenedor principal de las conjugaciones
    main_content = soup.find('div', class_='mw-content-ltr mw-parser-output')
    #print(main_content)
    
    # Si encuentra el párrafo "<p>Inusitée</p>" y el botón "<a class="mw-selflink selflink">Conjugaison pronominale</a>", activar la bandera only_promonimal
    only_promonimal = False
    for p in soup.find_all('p'):
        if p.get_text(strip=True) == "Inusitée":
            only_promonimal = True

    persons = []
    words = []
    
    if not main_content:
        return persons, words
    
    # Procesar cada sección de conjugaciones
    modes = []
    mode = None
    for section in main_content.find_all(['h3', 'table']):
        if section.name == 'h3':
            mode = section.get_text(strip=True)
            if mode == 'Modes impersonnels':
                mode = 'Impersonnel'
            modes.append(mode)
        
        elif section.name == 'table' and mode:
            # Si la bandera es false, obtener conjugaciones normalmente
            if not only_promonimal:    
                th_tr = soup.select('th[bgcolor], tr[bgcolor]')
                tenses = [t.text.strip() for t in th_tr if '#FFDDAA' not in t.get('bgcolor', [])]
            
                if th_tr:
                    tds_align_right = soup.select('td[align="right"], td[width="4.5%"], td[width="15%"]')
                    persons_temp = [td.text.strip().replace("\xa0"," ") for td in tds_align_right if 
                                        'API' not in td.get('class', [])]
                    persons = [obtener_persona(persona) for persona in persons_temp]
                    
                    tds_align_left = soup.select('td[align="left"], td[width="20%"]')
                    words = [td.text.strip() for td in tds_align_left if
                            'right' not in td.get('align', []) and
                            'API' not in td.get('class', [])]
            
            # Si la bandera es true, todo es igual excepto en las últimas tres persons y words
            # Ya que persons son
            # <td width="25%" align="left" style="white-space:nowrap">-toi&nbsp;</td>
            # <td width="25%" align="left" style="white-space:nowrap">-nous&nbsp;</td>
            # <td width="25%" align="left" style="white-space:nowrap">-vous&nbsp;</td>
            # Y words son
            # <td width="25%" align="right"><a href="/wiki/abeausis" title="abeausis">abeausis</a></td>
            # <td width="25%" align="right"><a href="/wiki/abeausissons" title="abeausissons">abeausissons</a></td>
            # <td width="25%" align="right"><a href="/wiki/abeausissez" title="abeausissez">abeausissez</a></td>
            if only_promonimal:
                th_tr = soup.select('th[bgcolor], tr[bgcolor]')
                tenses = [t.text.strip() for t in th_tr if '#FFDDAA' not in t.get('bgcolor', [])]
            
                if th_tr:
                    tds_align_right = soup.select('td[align="right"], td[width="4.5%"], td[width="15%"]')
                    persons_temp = [td.text.strip().replace("\xa0"," ") for td in tds_align_right if 
                                        'API' not in td.get('class', [])]
                    
                    # Reemplazar las últimas 3 entradas de persons_temp por las personas correctas
                    persons_temp[-3] = '-toi'
                    persons_temp[-2] = '-nous'
                    persons_temp[-1] = '-vous'
                    persons = [obtener_persona(persona) for persona in persons_temp]
                    
                    tds_align_left = soup.select('td[align="left"], td[width="20%"]')
                    words = [td.text.strip() for td in tds_align_left if
                            'right' not in td.get('align', []) and
                            'API' not in td.get('class', [])]
                    
                    # Reemplazar las últimas 3 entradas de words por las palabras correctas
                    # las cuales son los td que tienen align="right" y width="25%"
                    tds_align_left_promonimal = soup.select('td[align="right"][width="25%"]')
                    words[-3] = tds_align_left_promonimal[-3].text.strip()
                    words[-2] = tds_align_left_promonimal[-2].text.strip()
                    words[-1] = tds_align_left_promonimal[-1].text.strip()

    return persons, words

'''
# Impersonnel
[
"Présent", "Passé", "Présent", "Passé", "Présent", "Passé"
]

# Indicatif
[
"Présent", "Présent", "Présent", "Présent", "Présent", "Présent",
"Passé composé", "Passé composé", "Passé composé", "Passé composé", "Passé composé", "Passé composé",
"Imparfait", "Imparfait", "Imparfait", "Imparfait", "Imparfait", "Imparfait",
"Plus-que-parfait", "Plus-que-parfait", "Plus-que-parfait", "Plus-que-parfait", "Plus-que-parfait", "Plus-que-parfait",
"Passé simple", "Passé simple", "Passé simple", "Passé simple", "Passé simple", "Passé simple",
"Passé antérieur", "Passé antérieur", "Passé antérieur", "Passé antérieur", "Passé antérieur", "Passé antérieur",
"Futur simple", "Futur simple", "Futur simple", "Futur simple", "Futur simple", "Futur simple",
"Futur antérieur", "Futur antérieur", "Futur antérieur", "Futur antérieur", "Futur antérieur", "Futur antérieur"
]

# Subjonctif
[
"Présent", "Présent", "Présent", "Présent", "Présent", "Présent",
"Passé", "Passé", "Passé", "Passé", "Passé", "Passé",
"Imparfait", "Imparfait", "Imparfait", "Imparfait", "Imparfait", "Imparfait",
"Plus-que-parfait", "Plus-que-parfait", "Plus-que-parfait", "Plus-que-parfait", "Plus-que-parfait", "Plus-que-parfait"
]

# Conditionnel
[
"Présent", "Présent", "Présent", "Présent", "Présent", "Présent",
"Passé", "Passé", "Passé", "Passé", "Passé", "Passé"
]

# Impératif
[
"Présent", "Présent", "Présent",
"Passé", "Passé", "Passé",
]
'''
def generar_lista(personas_gramaticales, conjugaciones):
    indice = 0
    lista = []
    
    if personas_gramaticales == [] or conjugaciones == []:
        return []
    
    try: 
        # Impersonnel
        for categ in ["Infinitif", "Gérondif", "Participe"]:
            for elem in ["Présent", "Passé"]:
                lista.append({
                    "mode": categ.lower(), 
                    "tense": elem.lower(), 
                    "person": personas_gramaticales[indice], 
                    "word": conjugaciones[indice]
                })
                indice += 1

        # Indicatif
        for elem in ["Présent", "Passé composé", "Imparfait", "Plus-que-parfait", "Passé simple", "Passé antérieur", "Futur simple", "Futur antérieur"]:
            for i in range(6):
                lista.append({
                    "mode": "indicatif", 
                    "tense": elem.lower(), 
                    "person": personas_gramaticales[indice], 
                    "word": conjugaciones[indice]
                })
                indice += 1
            
        # Subjonctif
        for elem in ["Présent", "Passé", "Imparfait", "Plus-que-parfait"]:
            for i in range(6):
                lista.append({
                    "mode": "subjonctif", 
                    "tense": elem.lower(), 
                    "person": personas_gramaticales[indice], 
                    "word": conjugaciones[indice]
                })
                indice += 1

        # Conditionnel
        for elem in ["Présent", "Passé"]:
            for i in range(6):
                lista.append({
                    "mode": "conditionnel", 
                    "tense": elem.lower(), 
                    "person": personas_gramaticales[indice], 
                    "word": conjugaciones[indice]
                })
                indice += 1
                
        # Impératif
        for elem in ["Présent"]:
            for i in range(3):
                lista.append({
                    "mode": "impératif", 
                    "tense": elem.lower(), 
                    "person": personas_gramaticales[indice], 
                    "word": conjugaciones[indice]
                })
                indice += 1
        
        # Impératif no promonimal
        if indice < len(personas_gramaticales):
            for elem in ["Passé"]:
                for i in range(3):
                    lista.append({
                        "mode": "impératif", 
                        "tense": elem.lower(), 
                        "person": personas_gramaticales[indice], 
                        "word": conjugaciones[indice]
                    })
                    indice += 1

        return lista
    
    except IndexError:
        return []

def obtener_conjugaciones(url):
    personas_gramaticales, conjugaciones = descargar_html(url)
    return generar_lista(personas_gramaticales, conjugaciones)
