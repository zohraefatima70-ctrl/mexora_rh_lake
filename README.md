# Mexora RH Intelligence - Pipeline Data Lake

Bienvenue dans le projet Data Lake **Mexora RH Intelligence**.

Ce projet démontre l'architecture complète d'un Data Lake (Bronze, Silver, Gold) pour analyser le marché de l'emploi IT au Maroc.

## Comment exécuter le projet ?

Pour des raisons de taille et de propreté, les données générées ont été supprimées de ce dossier. Voici les étapes pour reproduire intégralement le projet depuis zéro :

### 1. Préparer l'environnement
Assurez-vous d'avoir Python installé (idéalement 3.9+). Installez les dépendances requises :
```bash
pip install -r requirements.txt
```

### 2. Générer les données brutes
Exécutez le script de génération de données. Cela va créer 5 000 offres d'emploi fictives réalistes (et y injecter des anomalies pour tester la robustesse du pipeline) dans le dossier `data/raw/` :
```bash
python data/generate_data.py
```

### 3. Exécuter le pipeline ETL (Data Lake)
Lancez le script principal pour faire passer les données à travers les zones Bronze, Silver, et Gold :
```bash
python main.py
```
*Le script va nettoyer, transformer, extraire les compétences via NLP et agréger les données dans des tables analytiques DuckDB au format Parquet.*

### 4. Analyser les résultats
Vous pouvez maintenant générer les graphiques d'analyse (qui s'enregistreront dans `analysis/output/`) :
```bash
python analysis/analyse_marche.py
```
Ou explorer les données de manière interactive en ouvrant le notebook Jupyter :
```bash
jupyter notebook analysis/analyse_marche_it_maroc.ipynb
```

## Documentation
- `conception_architecture.md` : Détaille l'architecture du projet.
- `rapport_pipeline.md` : Détaille les traitements et règles de gestion effectués à chaque étape du pipeline.
- `rapport_final_mexora.md` : Les insights business et RH extraits des données.
