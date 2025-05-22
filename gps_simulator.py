import tensorflow as tf
import pickle
import numpy as np
import pandas as pd
import os

model_path = './modele/traffic_model.h5'
scaler_path = './modele/scaler.pkl'
encoder_path = './modele/label_encoder.pkl'

if not os.path.exists(model_path) or \
        not os.path.exists(scaler_path) or \
        not os.path.exists(encoder_path):
    print("Erreur : Les fichiers du modèle (model.h5, scaler.pkl, label_encoder.pkl) sont introuvables.")
    print("Assurez-vous d'avoir exécuté 'creation_model.py' et que les chemins sont corrects.")
    exit()

try:
    model = tf.keras.models.load_model(model_path)
    with open(scaler_path, 'rb') as file:
        scaler = pickle.load(file)
    with open(encoder_path, 'rb') as file:
        label_encoder = pickle.load(file)
    print("Modèle, Scaler et LabelEncoder chargés avec succès.")
except Exception as e:
    print(f"Erreur lors du chargement des composants du modèle : {e}")
    exit()


def predict_traffic_state(hour, debit_horaire, taux_occupation):
    hour_sin = np.sin(hour * (2 * np.pi / 24))
    hour_cos = np.cos(hour * (2 * np.pi / 24))

    input_data = pd.DataFrame([[hour_sin, hour_cos, debit_horaire, taux_occupation]],
                              columns=['Heure_sin', 'Heure_cos', 'Debit horaire', 'Taux d\'occupation'])

    input_scaled = scaler.transform(input_data)
    prediction_proba = model.predict(input_scaled)
    predicted_class_index = np.argmax(prediction_proba, axis=1)
    predicted_traffic_state = label_encoder.inverse_transform(predicted_class_index)
    return predicted_traffic_state[0]


def simulate_gps_path(start_location, end_location, current_hour):
    print(f"\nSimulateur GPS : De '{start_location}' à '{end_location}' à {current_hour}h00")

    segments = [
        {'name': 'Segment A (entre départ et milieu)', 'debit_ex': 1200, 'taux_occ_ex': 0.6},
        {'name': 'Segment B (route principale)', 'debit_ex': 2500, 'taux_occ_ex': 0.8},
        {'name': 'Segment C (route alternative)', 'debit_ex': 800, 'taux_occ_ex': 0.3},
        {'name': 'Segment D (vers l\'arrivée)', 'debit_ex': 950, 'taux_occ_ex': 0.45},
    ]

    print("\nAnalyse du trafic sur les segments potentiels :")
    for segment in segments:
        predicted_state = predict_traffic_state(
            current_hour,
            segment['debit_ex'],
            segment['taux_occ_ex']
        )
        print(f"  - {segment['name']} : Trafic prédit à '{predicted_state}'")

    print("\nSuggestion de chemin (basée sur une logique simplifiée) :")

    if current_hour >= 7 and current_hour <= 9 or current_hour >= 16 and current_hour <= 19:  # Heures de pointe
        print("  C'est l'heure de pointe. Les routes principales (Segment B) risquent d'être très chargées.")
        print("  Il est recommandé de privilégier les routes alternatives (Segment C) si possible.")
        print("  Chemin suggéré : Passer par le Segment A, puis le Segment C, et enfin le Segment D.")
    else:
        print("  Le trafic semble être normal ou fluide.")
        print("  Chemin suggéré : Passer par le Segment A, puis le Segment B, et enfin le Segment D.")

    print("\nCeci est une simulation. Un vrai GPS utiliserait des cartes et des algorithmes de chemin plus complexes.")


if __name__ == "__main__":
    heure_actuelle = 17
    debit = 1500
    taux = 0.7

    etat_predit = predict_traffic_state(heure_actuelle, debit, taux)
    print(f"Prédiction de l'état du trafic pour {heure_actuelle}h, Débit: {debit}, Taux: {taux} : {etat_predit}")

    simulate_gps_path("Porte de Clignancourt", "Place d'Italie", heure_actuelle)