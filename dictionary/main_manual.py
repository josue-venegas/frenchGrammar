from tqdm import tqdm
from database_manager import create_database, insert_word, insert_category, insert_subcategory, associate_word_with_category, associate_word_with_subcategory, insert_conjugation, associate_word_with_conjugation

dictionary = {
    "Pronom":
        {
            "Sujet": 
                [
                    "Je", "Tu", "Il", "Elle", "On", "Nous", "Vous", "Ils", "Elles"
                ],
            "Adverbial":
                [
                    "En", "Y"
                ],
            "Tonique":
                [
                    "Moi", "Toi", "Lui", "Elle", "Nous", "Vous", "Eux", "Elles"
                ],
            "Complément d’objet direct":
                [
                    "Me", "M’", "Te", "T’", "Le", "L’", "La", "Nous", "Vous", "Les", "Les"
                ],
            "Complément d’object indirect":
                [
                    "Me", "M’", "Te", "T’", "Lui", "Lui", "Nous", "Vous", "Leur", "Leur"
                ],
            "Possessif":
                [
                    "Le mien", "La mienne", "Les miens", "Les miennes",
                    "Le tien", "La tienne", "Les tiens", "Les tiennes",
                    "Le sien", "La sienne", "Les siens", "Les siennes",
                    "Le nôtre", "La nôtre", "Les nôtres", "Les nôtres",
                    "Le vôtre", "La vôtre", "Les vôtres", "Les vôtres",
                    "Le leur", "La leur", "Les leurs", "Les leurs"
                ],
            "Réfléchi conjoint":
                [ 
                    "Me", "M’", "Te", "T’", "Se", "S’", "Nous", "Vous", "Se", "S’"
                ],
            "Réfléchi disjoint":
                [
                    "Moi", "Toi", "Lui", "Elle", "Soi", "Nous", "Vous", "Eux", "Elles", "Soi"
                ],
            "Relatif":
                [
                    "Qui", "Que", "Qu’", "Dont", "Où",
                    "Ce qui", "Ce que", "Ce dont",
                    "Lequel", "Lesquels", "Laquelle", "Lesquelles",
                    "Auquel", "À laquelle", "Auxquels", "Auxquelles",
                    "Duquel", "De laquelle", "Desquels", "Desquelles" 
                ],
            "Interrogatif":
                [
                    "Qui", "Que", "Quoi", "Quel", "Quelle", "Quels", "Quelles"
                ],
            "Démonstratif simple":
                [
                    "Celui", "Ceux", "Celle", "Celles", "Ce"
                ],
            "Démonstratif composé":
                [
                    "Celui-ci", "Celui-là", "Ceux-ci", "Ceux-là", "Celle-ci", "Celle-là", "Celles-ci", "Celles-là", "Ceci", "Cela", "Ça"
                ],
            "Indéfini":
                [
                    "Nul", "Nulle", "Personne", "Rien", "Aucun", "Aucune", "Aucuns", "Aucunes",
                    "Quelqu’un", "Quelqu’une", "Quelques-uns", "Quelques-unes",  "Quelque chose", "N’importe",
                    "Certain", "Certaine", "Certains", "Certaines", "Plusieurs", "La plupart", "Divers", "Diverses",
                    "Chacun", "Chacune", "Tout", "Toute", "Touts", "Toutes",
                    "Le même", "La même", "L’un", "L’une", "L’autre", "Les autres", "Tel", "Telle", "Tels", "Telles"
                ]
        },
    "Article": 
        {
            "Défini":
                [
                    "Le", "La", "L’", "Les"
                ],
            "Indéfini":
                [
                    "Un", "Une", "Des"
                ],
            "Partitif":
                [
                    "Du", "De la", "De l’", "Des"   
                ]
        },
    "Déterminant": 
        {
            "Possesif":
                [
                    "Mon", "Ma", "Mes",
                    "Ton", "Ta", "Tes",
                    "Son", "Sa", "Ses",
                    "Notre", "Notre", "Nos",
                    "Votre", "Votre", "Vos",
                    "Leur", "Leur", "Leurs"
                ],
            "Interrogatif":
                [
                    "Quel", "Quelle", "Quels", "Quelles"
                ],
            "Démonstratif":
                [
                    "Ce", "Cet", "Ces", "Cette", "Ces"
                ]
        },
    "Négation": 
        {
            "Général": 
                [
                    "Non", "Ne", "N’", "Pas"
                ],
        },
    "Ponctuation": 
        {
            "Général": 
                [
                    ",", "(", ")", "[", "]", "«", "»", "-", "/", 
                    ";", ":", ".", "...", "!", "?"
                ]
        },
    "Conjonction":
        {
            "Coordination":
                [
                    "et", "ou", "mais", "donc", "ni", "car"
                ]
        },
    "Adjectif":
        {
            "Indéfini":
                [
                    "chaque",
                ]
        }
}

# Crear la conexión a la base de datos
conn = create_database()

progress_bar = tqdm(desc="Guardando en base de datos", unit=" palabras guardadas")  # Configura la barra de progreso

for category, subcategories in dictionary.items():
    category_id = insert_category(conn, category.lower())
    for subcategory, words in subcategories.items():
        subcategory_id = insert_subcategory(conn, category_id, subcategory.lower())
        for word in words:
            progress_bar.update(1)
            progress_bar.set_postfix({"category": category, "subcategory": subcategory, "word": word})
            
            word_id = insert_word(conn, word)
            associate_word_with_category(conn, word_id, category_id)
            associate_word_with_subcategory(conn, word_id, subcategory_id)

progress_bar.set_postfix()  # Limpia los datos de la barra de progreso
progress_bar.close()  # Cierra la barra de progreso cuando se complete la desc

# Cierra la conexión cuando termines
conn.close()