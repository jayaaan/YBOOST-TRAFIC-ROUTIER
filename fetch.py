import requests
import pandas as pd

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

df = pd.json_normalize(all_data)

print("Valeurs manquantes par colonne :")
print(df.isnull().sum())

df.fillna(value={'q': 0, 'k': 0, 'date_debut': 'unknown', 'date_fin': 'unknown'}, inplace=True)

print(df.dtypes)

df['geo_point_2d'] = df['geo_point_2d'].apply(lambda x: str(x) if isinstance(x, list) else x)
df['geo_shape'] = df['geo_shape'].apply(lambda x: str(x) if isinstance(x, list) else x)
for col in df.columns:
    if df[col].apply(type).eq(list).any():
        df[col] = df[col].apply(lambda x: str(x) if isinstance(x, list) else x)
df = df.loc[:, df.columns.difference(['geo_point_2d', 'geo_shape'])]
df.drop_duplicates(inplace=True)
if 'some_column' in df.columns:
    df['some_column'] = df['some_column'].str.lower()

dataFile = "./data_cleaned.csv"
df.to_csv(dataFile, index=False)

print(f"Les données nettoyées ont été exportées ({len(df)} enregistrements)")