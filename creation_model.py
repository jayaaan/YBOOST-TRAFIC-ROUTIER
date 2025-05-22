import pandas as pd
import numpy as np
import pickle
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from keras.models import Sequential
from keras.layers import Dense

model_output_dir = './modele'
os.makedirs(model_output_dir, exist_ok=True)

file_path = './data/donnees_propres.csv'
try:
    data = pd.read_csv(file_path, sep=';')
except FileNotFoundError:
    print(f"Erreur : Le fichier '{file_path}' n'a pas été trouvé. Assurez-vous d'avoir exécuté 'preprocessing.py' en premier.")
    exit()

data['Heure_sin'] = np.sin(data['Heure'] * (2 * np.pi / 24))
data['Heure_cos'] = np.cos(data['Heure'] * (2 * np.pi / 24))

features = ['Heure_sin', 'Heure_cos', 'Debit horaire', 'Taux d\'occupation']
for feature in features:
    if feature not in data.columns:
        print(f"Erreur : La feature '{feature}' est manquante dans les données. Vérifiez vos étapes précédentes.")
        exit()

X = data[features]
y = data['Etat trafic']

label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)
print(f"Catégories d'état de trafic encodées : {label_encoder.classes_}")


X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

num_classes = np.unique(y_encoded).shape[0]
if num_classes < 2:
    print("Erreur : Moins de 2 classes uniques pour l'état du trafic. Le modèle ne peut pas être entraîné.")
    exit()

model = Sequential([
    Dense(128, activation='relu', input_shape=(X_train_scaled.shape[1],)),
    Dense(64, activation='relu'),
    Dense(num_classes, activation='softmax')
])

model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

print("\nDébut de l'entraînement du modèle...")
model.fit(X_train_scaled, y_train, epochs=10, validation_split=0.1, verbose=1)

print("\nÉvaluation du modèle sur l'ensemble de test...")
evaluation = model.evaluate(X_test_scaled, y_test, verbose=0)
print(f"Test loss: {evaluation[0]:.4f}, Test accuracy: {evaluation[1]:.4f}")

encoder_save_path = os.path.join(model_output_dir, 'label_encoder.pkl')
with open(encoder_save_path, 'wb') as file:
    pickle.dump(label_encoder, file)
print(f"LabelEncoder sauvegardé vers '{encoder_save_path}'")

scaler_save_path = os.path.join(model_output_dir, 'scaler.pkl')
with open(scaler_save_path, 'wb') as file:
    pickle.dump(scaler, file)
print(f"Scaler sauvegardé vers '{scaler_save_path}'")

model_save_path = os.path.join(model_output_dir, 'traffic_model.h5')
model.save(model_save_path)
print(f"Modèle sauvegardé vers '{model_save_path}'")