import pandas as pd
import os

file_path = './data/data_cleaned.csv'
output_dir = './data'
output_file_path = os.path.join(output_dir, 'donnees_propres.csv')

try:
    data = pd.read_csv(file_path, sep=';')
except FileNotFoundError:
    print(f"Erreur : Le fichier '{file_path}' n'a pas été trouvé. Assurez-vous d'avoir exécuté 'fetch.py' en premier.")
    exit()

print("Types de données avant correction :")
print(data.dtypes)

numeric_cols_to_check = ['Debit horaire', 'Taux d\'occupation']
for col in numeric_cols_to_check:
    if col in data.columns:
        data[col] = pd.to_numeric(data[col], errors='coerce')
        data.dropna(subset=[col], inplace=True)
    else:
        print(f"Attention : La colonne '{col}' n'existe pas dans le DataFrame.")

if 'Heure' in data.columns:
    data['Heure'] = pd.to_numeric(data['Heure'], errors='coerce').fillna(0).astype(int)
else:
    print("Attention : La colonne 'Heure' n'existe pas dans le DataFrame. Le modèle risque d'échouer.")

print("\nTypes de données après correction :")
print(data.dtypes)

data.to_csv(output_file_path, index=False, sep=';')

print(f"\nLes données nettoyées ont été exportées vers '{output_file_path}'")