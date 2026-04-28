# Mexora RH Intelligence — Data Lake Emploi IT Maroc

Pipeline complet Bronze/Silver/Gold pour analyser le marché de l'emploi IT marocain.

## Structure du projet

```
mexora_rh_lake/
├── data/
│   ├── raw/                          # Données brutes générées
│   │   ├── offres_emploi_it_maroc.json
│   │   ├── referentiel_competences_it.json
│   │   └── entreprises_it_maroc.csv
│   └── generate_data.py             # Générateur de données synthétiques
├── pipeline/
│   ├── bronze_ingestion.py          # Ingestion → Zone Bronze (JSON partitionné)
│   ├── silver_transform.py          # Nettoyage → Zone Silver (Parquet)
│   ├── silver_nlp.py                # Extraction compétences (NLP regex)
│   ├── gold_aggregation.py          # Agrégats analytiques → Gold (Parquet+DuckDB)
│   └── utils.py                     # Fonctions utilitaires partagées
├── analysis/
│   ├── analyse_marche.py            # 5 requêtes DuckDB + visualisations
│   └── output/                      # Graphiques générés
├── data_lake/
│   ├── bronze/                      # JSON bruts par source/mois
│   ├── silver/                      # Parquet nettoyés
│   └── gold/                        # Parquet analytiques
├── main.py                          # Orchestrateur du pipeline
└── requirements.txt
```

## Installation

```bash
pip install -r requirements.txt
```

## Exécution complète

```bash
# 1. Générer les données synthétiques
py -3 data/generate_data.py

# 2. Lancer le pipeline complet (Bronze → Silver → Gold)
py -3 main.py

# 3. Lancer l'analyse de marché
py -3 analysis/analyse_marche.py
```

## Architecture Data Lake

| Zone   | Format  | Partitionnement         | Usage                        |
|--------|---------|-------------------------|------------------------------|
| Bronze | JSON    | par_source / par_mois   | Archive immuable brute       |
| Silver | Parquet | offres_clean, comp.     | Données nettoyées typées     |
| Gold   | Parquet | tables analytiques      | KPIs, dashboards, rapports   |

## Tables Gold produites

| Table                     | Lignes | Description                          |
|---------------------------|--------|--------------------------------------|
| top_competences.parquet   | 196    | Compétences par profil, famille, rang |
| salaires_par_profil.parquet| 371   | Médiane/Q1/Q3 salaires par profil+ville|
| offres_par_ville.parquet  | 1930   | Volume offres + % remote par ville   |
| entreprises_recruteurs.parquet| 100 | Top 100 entreprises recruteurs      |
| tendances_mensuelles.parquet| 322  | Évolution mensuelle 2023-2024        |

## Résultats pipeline

- **Bronze** : 5 000 offres → 69 fichiers partitionnés (rekrute/linkedin/marocannonce)
- **Silver** : 5 000 offres nettoyées + 26 711 lignes compétences extraites
- **Gold** : 5 tables analytiques prêtes pour DuckDB / Power BI
- **Durée** : ~15 secondes sur machine locale

## Stack technique

- Python 3.11+ | pandas | pyarrow | duckdb | matplotlib | seaborn | plotly
