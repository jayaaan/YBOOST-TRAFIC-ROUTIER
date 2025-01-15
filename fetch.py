import requests
import pandas as pd

url = "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/comptages-routiers-permanents/records?limit=-1"
response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    df = pd.json_normalize(data['results'])

    dataFile = "./data.csv"

    df.to_csv(dataFile, index=False)

    print("Les données ont été exportées")
else:
    print("Erreur lors de la récupération des données ", response.status_code)