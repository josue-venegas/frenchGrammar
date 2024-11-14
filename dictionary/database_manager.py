import sqlite3
from typing import Tuple, Optional

# Función para conectar y crear la base de datos y sus tablas
def create_database():
    conn = sqlite3.connect('dictionary.db')
    cursor = conn.cursor()

    # Crear la tabla de palabras
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS word (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word TEXT NOT NULL UNIQUE
        );
    ''')
    
    # Crear la tabla de categorías
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS category (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        );
    ''')

    # Crear la tabla de subcategorías
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subcategory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category_id INTEGER,
            FOREIGN KEY (category_id) REFERENCES category(id),
            UNIQUE(name, category_id)
        );
    ''')
    
    # Crear la tabla de conjugaciones
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conjugation (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conjugated_form TEXT,
            tense TEXT,
            mood TEXT,
            person TEXT,
            UNIQUE(conjugated_form, tense, mood, person)
        );
    ''')

    # Crear la tabla intermedia para asociar palabras con categorías
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS word_category (
            word_id INTEGER,
            category_id INTEGER,
            FOREIGN KEY (word_id) REFERENCES word(id),
            FOREIGN KEY (category_id) REFERENCES category(id),
            PRIMARY KEY (word_id, category_id)
        );
    ''')

    # Crear la tabla intermedia para asociar palabras con subcategorías
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS word_subcategory (
            word_id INTEGER,
            subcategory_id INTEGER,
            FOREIGN KEY (word_id) REFERENCES word(id),
            FOREIGN KEY (subcategory_id) REFERENCES subcategory(id),
            PRIMARY KEY (word_id, subcategory_id)
        );
    ''')
    
    # Crear la tabla intermedia para asociar palabras con conjugaciones
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS word_conjugation (
            word_id INTEGER,
            conjugation_id INTEGER,
            FOREIGN KEY (word_id) REFERENCES word(id),
            FOREIGN KEY (conjugation_id) REFERENCES conjugation(id),
            PRIMARY KEY (word_id, conjugation_id)
        );
    ''')

    conn.commit()
    return conn

# Función para insertar una palabra
def insert_word(conn, word: str) -> int:
    cursor = conn.cursor()
    
    # Verificar si la palabra ya existe
    cursor.execute('SELECT id FROM word WHERE word = ?', (word,))
    result = cursor.fetchone()
    
    if result:
        # Si la palabra ya existe, devuelve su id
        return result[0]
    
    # Si no existe, inserta la palabra
    cursor.execute('INSERT INTO word (word) VALUES (?)', (word,))
    conn.commit()
    return cursor.lastrowid
    
# Función para insertar una categoría
def insert_category(conn, name: str) -> int:
    cursor = conn.cursor()
    
    # Verificar si la categoría ya existe
    cursor.execute('SELECT id FROM category WHERE name = ?', (name,))
    result = cursor.fetchone()
    
    if result:
        # Si la categoría ya existe, devuelve su id
        return result[0]
    
    # Si no existe, inserta la categoría
    cursor.execute('INSERT INTO category (name) VALUES (?)', (name,))
    conn.commit()
    return cursor.lastrowid

# Función para insertar una subcategoría
def insert_subcategory(conn, category_id: int, name: str) -> int:
    cursor = conn.cursor()
    
    # Verificar si la subcategoría ya existe
    cursor.execute('SELECT id FROM subcategory WHERE name = ? AND category_id = ?', (name, category_id))
    result = cursor.fetchone()
    
    if result:
        # Si la subcategoría ya existe, devuelve su id
        return result[0]
    
    # Si no existe, inserta la subcategoría
    cursor.execute('INSERT INTO subcategory (name, category_id) VALUES (?, ?)', (name, category_id))
    conn.commit()
    return cursor.lastrowid

# Función para insertar una conjugación
def insert_conjugation(conn, conjugated_form: str, tense: str, mood: str, person: str) -> int:
    cursor = conn.cursor()
    
    # Verificar si la conjugación ya existe para el word_id
    cursor.execute('''
        SELECT id FROM conjugation 
        WHERE conjugated_form = ? AND tense = ? AND mood = ? AND person = ?
    ''', (conjugated_form, tense, mood, person))
    result = cursor.fetchone()
    
    if result:
        # Si ya existe, devuelve su id
        return result[0]
    
    # Si no existe, inserta la conjugación
    cursor.execute('''
        INSERT INTO conjugation (conjugated_form, tense, mood, person) 
        VALUES (?, ?, ?, ?)
    ''', (conjugated_form, tense, mood, person))
    conn.commit()
    return cursor.lastrowid

# Función para insertar una subcategoría
def associate_word_with_category(conn, word_id: int, category_id: int):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO word_category (word_id, category_id) 
        VALUES (?, ?)
    ''', (word_id, category_id))
    conn.commit()

# Función para asociar una palabra a una subcategoría
def associate_word_with_subcategory(conn, word_id: int, subcategory_id: int):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO word_subcategory (word_id, subcategory_id) 
        VALUES (?, ?)
    ''', (word_id, subcategory_id))
    conn.commit()
    
# Función para asociar una palabra a una conjugación
def associate_word_with_conjugation(conn, word_id: int, conjugation_id: int):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO word_conjugation (word_id, conjugation_id) 
        VALUES (?, ?)
    ''', (word_id, conjugation_id))
    conn.commit()


if __name__ == '__main__':
    conn = create_database()
    
    # Ejemplo: La palabra "une" es un sustantivo, un adjetivo, un artículo y un pronombre
    word_id = insert_word(conn, 'une')

    nom_category_id = insert_category(conn, 'nom')
    adjectif_category_id = insert_category(conn, 'adjectif')
    article_category_id = insert_category(conn, 'article')
    pronom_category_id = insert_category(conn, 'pronom')

    
    nom_commune_subcategory_id = insert_subcategory(conn, nom_category_id, 'commun')
    adjectif_numéral_subcategory_id = insert_subcategory(conn, adjectif_category_id, 'numéral')
    article_indéfini_subcategory_id = insert_subcategory(conn, article_category_id, 'indéfini')
    pronom_indéfini_subcategory_id = insert_subcategory(conn, pronom_category_id, 'indéfini')

    
    associate_word_with_category(conn, word_id, nom_category_id)
    associate_word_with_category(conn, word_id, adjectif_category_id)
    associate_word_with_category(conn, word_id, article_category_id)
    associate_word_with_category(conn, word_id, pronom_category_id)

    associate_word_with_subcategory(conn, word_id, nom_commune_subcategory_id)
    associate_word_with_subcategory(conn, word_id, adjectif_numéral_subcategory_id)
    associate_word_with_subcategory(conn, word_id, article_indéfini_subcategory_id)
    associate_word_with_subcategory(conn, word_id, pronom_indéfini_subcategory_id)
    
    # Ejemplo: La palabra "manger" es un verbo y un sustantivo
    word_id = insert_word(conn, 'manger')
    
    verbe_category_id = insert_category(conn, 'verbe')
    associate_word_with_category(conn, word_id, verbe_category_id)

    conj_pre_ind_1 = insert_conjugation(conn, "mange", "présent", "indicatif", "1ère personne du singulier")
    conj_pre_ind_2 = insert_conjugation(conn, "manges", "présent", "indicatif", "2ème personne du singulier")
    conj_pre_ind_3 = insert_conjugation(conn, "mange", "présent", "indicatif", "3ème personne du singulier")
    conj_pre_ind_4 = insert_conjugation(conn, "mangeons", "présent", "indicatif", "1ère personne du pluriel")
    conj_pre_ind_5 = insert_conjugation(conn, "mangez", "présent", "indicatif", "2ème personne du pluriel")
    conj_pre_ind_6 = insert_conjugation(conn, "mangent", "présent", "indicatif", "3ème personne du pluriel")
    
    conj_fut_ind_1 = insert_conjugation(conn, "mangerai", "futur", "indicatif", "1ère personne du singulier")
    conj_fut_ind_2 = insert_conjugation(conn, "mangeras", "futur", "indicatif", "2ème personne du singulier")
    conj_fut_ind_3 = insert_conjugation(conn, "mangera", "futur", "indicatif", "3ème personne du singulier")
    conj_fut_ind_4 = insert_conjugation(conn, "mangerons", "futur", "indicatif", "1ère personne du pluriel")
    conj_fut_ind_5 = insert_conjugation(conn, "mangerez", "futur", "indicatif", "2ème personne du pluriel")
    conj_fut_ind_6 = insert_conjugation(conn, "mangeront", "futur", "indicatif", "3ème personne du pluriel")
    
    associate_word_with_conjugation(conn, word_id, conj_pre_ind_1)
    associate_word_with_conjugation(conn, word_id, conj_pre_ind_2)
    associate_word_with_conjugation(conn, word_id, conj_pre_ind_3)
    associate_word_with_conjugation(conn, word_id, conj_pre_ind_4)
    associate_word_with_conjugation(conn, word_id, conj_pre_ind_5)
    associate_word_with_conjugation(conn, word_id, conj_pre_ind_6)
    
    associate_word_with_conjugation(conn, word_id, conj_fut_ind_1)
    associate_word_with_conjugation(conn, word_id, conj_fut_ind_2)
    associate_word_with_conjugation(conn, word_id, conj_fut_ind_3)
    associate_word_with_conjugation(conn, word_id, conj_fut_ind_4)
    associate_word_with_conjugation(conn, word_id, conj_fut_ind_5)
    associate_word_with_conjugation(conn, word_id, conj_fut_ind_6)
    
    nom_category_id = insert_category(conn, 'nom')
    nom_commune_subcategory_id = insert_subcategory(conn, nom_category_id, 'commun')
    
    associate_word_with_category(conn, word_id, nom_category_id)
    associate_word_with_subcategory(conn, word_id, nom_commune_subcategory_id)
    
    conn.close()