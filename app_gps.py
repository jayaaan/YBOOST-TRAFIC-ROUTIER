import streamlit as st
import pandas as pd
import numpy as np
import pickle
import os
import folium
from streamlit_folium import folium_static
from geopy.geocoders import Nominatim
from tensorflow.keras.models import load_model

st.set_page_config(layout="wide", page_title="Simulateur GPS de Trafic")

st.title("🗺️ Simulateur GPS avec Prédiction de Trafic")
st.write("Entrez les informations pour simuler un trajet et prédire l'état du trafic.")

model_dir = './modele'
model_path = os.path.join(model_dir, 'traffic_model.h5')
scaler_path = os.path.join(model_dir, 'scaler.pkl')
label_encoder_path = os.path.join(model_dir, 'label_encoder.pkl')

try:
    model = load_model(model_path)
    with open(scaler_path, 'rb') as f:
        scaler = pickle.load(f)
    with open(label_encoder_path, 'rb') as f:
        label_encoder = pickle.load(f)
    st.sidebar.success("Modèle, Scaler et LabelEncoder chargés avec succès.")
except Exception as e:
    st.sidebar.error(
        f"Erreur lors du chargement des composants du modèle : {e}. Assurez-vous d'avoir exécuté 'creation_model.py'.")
    st.stop()


def predict_traffic_state(heure, debit, taux, model, scaler, label_encoder):
    heure_sin = np.sin(heure * (2 * np.pi / 24))
    heure_cos = np.cos(heure * (2 * np.pi / 24))

    features = np.array([[heure_sin, heure_cos, debit, taux]])
    features_scaled = scaler.transform(features)

    prediction_proba = model.predict(features_scaled)
    predicted_class_index = np.argmax(prediction_proba, axis=1)[0]
    predicted_label = label_encoder.inverse_transform([predicted_class_index])[0]
    return predicted_label


st.header("Prédiction de l'état du trafic pour un point donné")

col1, col2, col3 = st.columns(3)
with col1:
    input_heure = st.slider("Heure de la journée (0-23h)", 0, 23, 17)
with col2:
    input_debit = st.number_input("Débit horaire (nombre de véhicules)", 0, 5000, 1500)
with col3:
    input_taux = st.number_input("Taux d'occupation (0.0 - 1.0)", 0.0, 1.0, 0.7, step=0.01)

if st.button("Prédire l'état du trafic"):
    etat_predit = predict_traffic_state(input_heure, input_debit, input_taux, model, scaler, label_encoder)
    st.success(f"**Prédiction de l'état du trafic : {etat_predit}**")

st.markdown("---")

st.header("Simulateur de Trajet GPS")

start_address = st.text_input("Adresse de départ", "Tour Eiffel, Paris")
end_address = st.text_input("Adresse d'arrivée", "Cathédrale Notre-Dame de Paris")
heure_trajet = st.slider("Heure du trajet (pour la simulation)", 0, 23, 17)

geolocator = Nominatim(user_agent="traffic_simulator_app")

if st.button("Simuler le trajet"):
    start_location = None
    end_location = None

    with st.spinner("Recherche des adresses..."):
        try:
            start_location = geolocator.geocode(start_address, timeout=10)
            end_location = geolocator.geocode(end_address, timeout=10)
        except Exception as e:
            st.error(f"Erreur de géocodage : {e}. Assurez-vous que les adresses sont valides.")

    if start_location and end_location:
        st.success(
            f"Départ: {start_location.address} (Lat: {start_location.latitude}, Lon: {start_location.longitude})")
        st.success(f"Arrivée: {end_location.address} (Lat: {end_location.latitude}, Lon: {end_location.longitude})")

        m = folium.Map(location=[(start_location.latitude + end_location.latitude) / 2,
                                 (start_location.longitude + end_location.longitude) / 2],
                       zoom_start=12)

        folium.Marker([start_location.latitude, start_location.longitude],
                      popup=f"Départ: {start_address}", icon=folium.Icon(color='green', icon='play')).add_to(m)
        folium.Marker([end_location.latitude, end_location.longitude],
                      popup=f"Arrivée: {end_address}", icon=folium.Icon(color='red', icon='stop')).add_to(m)

        folium.PolyLine([(start_location.latitude, start_location.longitude),
                         (end_location.latitude, end_location.longitude)],
                        color="blue", weight=2.5, opacity=1, tooltip="Chemin Direct").add_to(m)

        st.subheader(f"Analyse du trafic sur les segments potentiels à {heure_trajet}h00 :")

        segments = [
            {"name": "Segment A (entre départ et milieu)", "debit_ex": 800, "taux_occ_ex": 0.3},
            {"name": "Segment B (route principale)", "debit_ex": 1800, "taux_occ_ex": 0.8},
            {"name": "Segment C (route alternative)", "debit_ex": 600, "taux_occ_ex": 0.2},
            {"name": "Segment D (vers l'arrivée)", "debit_ex": 950, "taux_occ_ex": 0.45},
        ]

        segment_predictions = {}
        for segment in segments:
            predicted_state = predict_traffic_state(
                heure_trajet, segment["debit_ex"], segment["taux_occ_ex"], model, scaler, label_encoder
            )
            segment_predictions[segment["name"]] = predicted_state
            st.write(f"  - {segment['name']} : Trafic prédit à '**{predicted_state}**'")

        st.markdown("---")
        st.subheader("Suggestion de chemin :")

        fluide_count = sum(1 for state in segment_predictions.values() if state == 'Fluide')
        sature_count = sum(1 for state in segment_predictions.values() if state == 'Saturé')

        suggestion = ""
        if sature_count > fluide_count and heure_trajet >= 7 and heure_trajet <= 20:
            suggestion = "Il semble y avoir du trafic sur les routes principales. Il est recommandé de privilégier les routes alternatives."
            chemin_suggerer = "Passer par le Segment A, puis le Segment C, et enfin le Segment D."
        elif fluide_count > sature_count:
            suggestion = "Le trafic semble fluide. Le chemin direct pourrait être optimal."
            chemin_suggerer = "Passer par le Segment A, puis le Segment B, et enfin le Segment D."
        else:
            suggestion = "Les conditions de trafic sont variées ou inconnues sur certains segments. Une vigilance particulière est requise."
            chemin_suggerer = "Considérez les prédictions individuelles pour chaque segment."

        st.info(suggestion)
        st.write(f"**Chemin suggéré :** {chemin_suggerer}")

        folium_static(m)

    else:
        st.warning("Veuillez entrer des adresses de départ et d'arrivée valides.")