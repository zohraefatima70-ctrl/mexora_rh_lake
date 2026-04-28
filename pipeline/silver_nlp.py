"""
Silver NLP Pipeline
Extraction des competences IT depuis le texte libre.
"""
import re
import json
import pandas as pd
from pathlib import Path


def extraire_competences(df: pd.DataFrame, referentiel_path: str) -> pd.DataFrame:
    """
    Extrait les competences IT depuis deux sources :
      1. Le champ 'competences_brut' (liste semi-structuree)
      2. Le champ 'description' (texte libre)

    Strategie : matching sur le referentiel de competences normalise.
    Chaque offre produit une ligne par competence detectee.
    """
    with open(referentiel_path, 'r', encoding='utf-8') as f:
        referentiel = json.load(f)

    # Construire un dictionnaire plat : alias -> nom_normalise, famille
    dict_competences = {}
    for famille, competences in referentiel['familles'].items():
        for nom_normalise, aliases in competences.items():
            for alias in aliases:
                dict_competences[alias.lower()] = {
                    'competence': nom_normalise,
                    'famille': famille
                }

    # Trier par longueur decroissante pour eviter les faux positifs
    aliases_tries = sorted(dict_competences.keys(), key=len, reverse=True)

    resultats = []

    for _, offre in df.iterrows():
        # Concatener les deux sources de texte
        texte_complet = ' '.join(filter(None, [
            str(offre.get('competences_brut', '') or ''),
            str(offre.get('description', '') or '')
        ])).lower()

        competences_trouvees = set()

        for alias in aliases_tries:
            # Recherche en tant que mot entier (word boundary)
            pattern = r'\b' + re.escape(alias) + r'\b'
            if re.search(pattern, texte_complet):
                info = dict_competences[alias]
                cle = info['competence']
                if cle not in competences_trouvees:
                    competences_trouvees.add(cle)
                    resultats.append({
                        'id_offre':   offre['id_offre'],
                        'profil':     offre.get('profil_normalise'),
                        'ville':      offre.get('ville_std'),
                        'competence': info['competence'],
                        'famille':    info['famille'],
                        'date_pub':   offre.get('date_publication'),
                        'annee':      offre.get('annee'),
                        'mois':       offre.get('mois'),
                    })

        # Offre sans competence detectee
        if not competences_trouvees:
            resultats.append({
                'id_offre':   offre['id_offre'],
                'profil':     offre.get('profil_normalise'),
                'ville':      offre.get('ville_std'),
                'competence': 'non_detecte',
                'famille':    'inconnu',
                'date_pub':   offre.get('date_publication'),
                'annee':      offre.get('annee'),
                'mois':       offre.get('mois'),
            })

    df_competences = pd.DataFrame(resultats)

    nb_offres_avec = df_competences[df_competences['competence'] != 'non_detecte']['id_offre'].nunique()
    print(f"[SILVER NLP] {len(df_competences)} lignes competences extraites")
    print(f"[SILVER NLP] {nb_offres_avec}/{len(df)} offres ont au moins 1 competence detectee")

    return df_competences


def sauvegarder_silver(df_offres: pd.DataFrame, df_competences: pd.DataFrame,
                       data_lake_root: str):
    """Sauvegarde les donnees Silver au format Parquet."""
    silver_path = Path(data_lake_root) / 'silver'

    # Offres nettoyees
    chemin_offres = silver_path / 'offres_clean' / 'offres_clean.parquet'
    chemin_offres.parent.mkdir(parents=True, exist_ok=True)
    df_offres.to_parquet(chemin_offres, index=False, compression='snappy')
    size_ko = chemin_offres.stat().st_size // 1024
    print(f"[SILVER] offres_clean.parquet sauvegarde ({size_ko} Ko)")

    # Competences extraites
    chemin_comp = silver_path / 'competences_extraites' / 'competences.parquet'
    chemin_comp.parent.mkdir(parents=True, exist_ok=True)
    df_competences.to_parquet(chemin_comp, index=False, compression='snappy')
    size_ko = chemin_comp.stat().st_size // 1024
    print(f"[SILVER] competences.parquet sauvegarde ({size_ko} Ko)")
