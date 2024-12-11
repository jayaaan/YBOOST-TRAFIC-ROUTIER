import requests

api_url = "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/comptages-routiers-permanents/records?limit=20"

response = requests.get(api_url)
if response.status_code == 200 :
    data = response.json()
    print(data)