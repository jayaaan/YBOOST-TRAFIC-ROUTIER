from pymongo import MongoClient
import pandas as pd

client = MongoClient('mongodb+srv://jayanilangovane:jayanthanos3@cluster0.to8rw.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')

db = client.yboost['data']
collection = db.yboost['cleaned-data']

csv_file_path = "C:\Etudes-informatiques\Yboost\YBOOST-TRAFIC-ROUTIER\data_cleaned.csv"

def import_csv_to_mongodb(csv_file_path, collection):
    # Lire le fichier CSV avec pandas
    data = pd.read_csv(csv_file_path)

    # Convertir le DataFrame en dictionnaire
    data_dict = data.to_dict(orient="records")

    # Insérer les données dans la collection
    collection.insert_many(data_dict)

    print(f"{len(data_dict)} documents insérés dans la collection {collection.name}.")

# Appeler la fonction pour importer le fichier CSV
import_csv_to_mongodb(csv_file_path, collection)