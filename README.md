Pour récupérer le projet:

```bash
git clone https://github.com/jayaaan/YBOOST-TRAFIC-ROUTIER

conda install -c conda-forge numpy=1.26 pandas scikit-learn scipy numexpr bottleneck tensorflow streamlit folium geopy streamlit-folium
```

Pour lancer le projet:

```bash
python Workspace.py

python automatiser_l_insertion_db.py

python prepocessing.py

python creation_model.py

streamlit run app_gps.py

```

Structure du Projet

Les données sont dans le dossier ```data``` et sauvegardées sous le format csv.

Le dossier model contient scaler.pkl, label_encoder.pkl et traffic_model.h5.
