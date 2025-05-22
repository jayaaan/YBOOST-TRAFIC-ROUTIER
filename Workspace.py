import requests
import pandas as pd
import os

output_dir = './data'
os.makedirs(output_dir, exist_ok=True)

url = "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/comptages-routiers-permanents/records"
all_data = []
params = {
    'limit': 100,
    'offset': 0,
    'order_by': 't_1h DESC'
}
max_records = 10000

print("Début de la récupération des données...")
while True:
    if params['offset'] >= max_records:
        print(f"Limite de {max_records} enregistrements atteinte.")
        break

    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if not data['results']:
            print("Aucun résultat retourné par l'API pour les critères de filtre actuels.")
            break

        all_data.extend(data['results'])
        params['offset'] += params['limit']
        print(f"  Récupéré {len(all_data)} enregistrements...")
    else:
        print(f"Erreur lors de la récupération des données : {response.status_code}")
        print("Détails de la réponse : ", response.text)
        break

df = pd.json_normalize(all_data)

print("\nColonnes brutes après json_normalize (AVANT RENOMMAGE et traitement):")
print(df.columns.tolist())
print("-" * 50)

if df.empty:
    print("Le DataFrame est vide. Aucune donnée à traiter. Veuillez vérifier les paramètres de récupération de l'API.")
    exit()

columns_to_rename_map = {
    'q': 'Debit horaire',
    'k': 'Taux d\'occupation',
    't_1h': 'Heure',
    'etat_trafic': 'Etat trafic'
}

df.rename(
    columns={old_name: new_name for old_name, new_name in columns_to_rename_map.items() if old_name in df.columns},
    inplace=True)

if 'Heure' in df.columns:
    df['Heure'] = pd.to_datetime(df['Heure'], errors='coerce').dt.hour
    # Remplacer les NaN qui pourraient apparaître si la conversion échoue
    df['Heure'].fillna(-1, inplace=True)  # Utilise -1 ou une autre valeur pour indiquer une erreur/absence d'heure
    df = df[df['Heure'] != -1]  # Supprime les lignes où l'heure n'a pas pu être extraite
else:
    print("ERREUR GRAVE: La colonne 'Heure' (ex-'t_1h') est manquante. Le modèle ne pourra pas fonctionner.")
    exit()

if 'Debit horaire' in df.columns:
    df['Debit horaire'] = pd.to_numeric(df['Debit horaire'], errors='coerce').fillna(0)
else:
    print("ERREUR GRAVE: La colonne 'Debit horaire' (ex-'q') est manquante. Le modèle ne pourra pas fonctionner.")
    exit()

if 'Taux d\'occupation' in df.columns:
    df['Taux d\'occupation'] = pd.to_numeric(df['Taux d\'occupation'], errors='coerce').fillna(0)
else:
    print("ERREUR GRAVE: La colonne 'Taux d\'occupation' (ex-'k') est manquante. Le modèle ne pourra pas fonctionner.")
    exit()

if 'Etat trafic' in df.columns:
    df['Etat trafic'].fillna('Inconnu', inplace=True)
else:
    print("ERREUR GRAVE: La colonne 'Etat trafic' est manquante. Le modèle ne pourra pas fonctionner.")
    exit()

columns_to_keep_final = [
    'Heure',
    'Debit horaire',
    'Taux d\'occupation',
    'Etat trafic'
]

df = df[list(set(columns_to_keep_final) & set(df.columns))]

df.drop_duplicates(inplace=True)

dataFile = os.path.join(output_dir, "data_cleaned.csv")
df.to_csv(dataFile, index=False, sep=';')

print(f"\nLes données nettoyées ont été exportées vers '{dataFile}' ({len(df)} enregistrements)")
print("\nTypes de données finales dans le CSV exporté:")
print(df.dtypes)