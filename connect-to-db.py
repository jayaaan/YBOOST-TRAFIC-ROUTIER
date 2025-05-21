<<<<<<< HEAD
import requests
from pymongo import MongoClient
import pandas as pd

# Connexion à MongoDB
client = MongoClient('mongodb+srv://jayanilangovane:jayanthanos3@cluster0.hf6laal.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client.yboost2_1  # Utilisez la nouvelle base de données
collection = db.cleaned_data  # Utilisez la collection souhaitée

url = "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/comptages-routiers-permanents/records"
all_data = []
params = {'limit': 100, 'offset': 0}
max_records = 10000

while True:
    if params['offset'] + params['limit'] > max_records:
        params['limit'] = max_records - params['offset']

    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if not data['results']:
            break
        all_data.extend(data['results'])
        params['offset'] += params['limit']
    else:
        print("Erreur lors de la récupération des données ", response.status_code)
        print("Détails de la réponse : ", response.text)
        break

# Convertir les données en DataFrame
df = pd.json_normalize(all_data)

# Remplir les valeurs manquantes
df.fillna(value={'q': 0, 'k': 0, 'date_debut': 'unknown', 'date_fin': 'unknown'}, inplace=True)

# Convertir les listes en chaînes de caractères
df['geo_point_2d'] = df['geo_point_2d'].apply(lambda x: str(x) if isinstance(x, list) else x)
df['geo_shape'] = df['geo_shape'].apply(lambda x: str(x) if isinstance(x, list) else x)
for col in df.columns:
    if df[col].apply(type).eq(list).any():
        df[col] = df[col].apply(lambda x: str(x) if isinstance(x, list) else x)

# Supprimer les colonnes non nécessaires
df = df.loc[:, df.columns.difference(['geo_point_2d', 'geo_shape'])]

# Supprimer les doublons
df.drop_duplicates(inplace=True)

# Convertir le DataFrame en dictionnaire
data_dict = df.to_dict(orient="records")

# Insérer les données dans la collection MongoDB
collection.insert_many(data_dict)

print(f"{len(data_dict)} documents insérés dans la collection {collection.name}.")
=======
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
>>>>>>> 1581b3cb5744bcae23feecce96623ce82be828f6
