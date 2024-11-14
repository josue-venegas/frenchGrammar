from tqdm import tqdm
from word_downloader import load_words
from word_categorizer import obtener_subcategorias
from word_conjugator import obtener_conjugaciones
from database_manager import create_database, insert_word, insert_category, insert_subcategory, associate_word_with_category, associate_word_with_subcategory, insert_conjugation, associate_word_with_conjugation

# URLs for fetching words from different grammatical categories
api_urls = {
    "adjectif": 'https://fr.wiktionary.org/w/api.php?action=query&list=categorymembers&cmtitle=Catégorie:Adjectifs_en_français&cmlimit=100&cmnamespace=0&format=json&origin=*',
    "adverbe": 'https://fr.wiktionary.org/w/api.php?action=query&list=categorymembers&cmtitle=Catégorie:Adverbes_en_français&cmlimit=100&cmnamespace=0&format=json&origin=*',
    "conjonction": 'https://fr.wiktionary.org/w/api.php?action=query&list=categorymembers&cmtitle=Catégorie:Conjonctions_en_français&cmlimit=100&cmnamespace=0&format=json&origin=*',
    "déterminant": 'https://fr.wiktionary.org/w/api.php?action=query&list=categorymembers&cmtitle=Catégorie:Déterminants_en_français&cmlimit=100&cmnamespace=0&format=json&origin=*',
    "interjection": 'https://fr.wiktionary.org/w/api.php?action=query&list=categorymembers&cmtitle=Catégorie:Interjections_en_français&cmlimit=100&cmnamespace=0&format=json&origin=*',
    "nom": 'https://fr.wiktionary.org/w/api.php?action=query&list=categorymembers&cmtitle=Catégorie:Noms_communs_en_français&cmlimit=100&cmnamespace=0&format=json&origin=*',    
    "nom_2": 'https://fr.wiktionary.org/w/api.php?action=query&list=categorymembers&cmtitle=Catégorie:Noms_propres_en_français&cmlimit=100&cmnamespace=0&format=json&origin=*',
    "préposition": 'https://fr.wiktionary.org/w/api.php?action=query&list=categorymembers&cmtitle=Catégorie:Prépositions_en_français&cmlimit=100&cmnamespace=0&format=json&origin=*',
    "verbe": 'https://fr.wiktionary.org/w/api.php?action=query&list=categorymembers&cmtitle=Catégorie:Verbes_en_français&cmlimit=100&cmnamespace=0&format=json&origin=*',
}

# Crear la conexión a la base de datos
conn = create_database()

progress_bar = tqdm(desc="Guardando en base de datos", unit=" palabras guardadas")  # Configura la barra de progreso

# Descargar palabras
for category, url in api_urls.items():       
    
    if category == "nom_2":
        category = "nom"

    words = load_words(url, category)

    # Obtener las subcategorías (adjetivo: calificativo, demostrativo, etc.)
    for word in words:
        progress_bar.update(1)
        progress_bar.set_postfix({"category": category, "word": word})
        
        word_id = insert_word(conn, word)
        category_id = insert_category(conn, category.lower())
        associate_word_with_category(conn, word_id, category_id)
        
        subcategories = obtener_subcategorias(word, category)
        for subcategory in subcategories:
            subcategory_id = insert_subcategory(conn, category_id, subcategory.lower())
            associate_word_with_subcategory(conn, word_id, subcategory_id)
        
        if category == "verbe":
            base_url = 'https://fr.wiktionary.org/wiki/Conjugaison:français/'
            conjugations = obtener_conjugaciones(base_url + word)
            
            for conjugation in conjugations:
                progress_bar.set_postfix({"category": category, "word": word, "conjugation": conjugation["word"]})
                conjugation_id = insert_conjugation(conn, conjugation["word"], conjugation["tense"], conjugation["mode"], conjugation["person"])
                associate_word_with_conjugation(conn, word_id, conjugation_id)

progress_bar.set_postfix()  # Limpia los datos de la barra de progreso    
progress_bar.close()  # Cierra la barra de progreso cuando se complete la descarga
  
# Cierra la conexión cuando termines
conn.close()