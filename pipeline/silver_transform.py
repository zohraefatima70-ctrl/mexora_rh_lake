"""
Silver Transform Pipeline
Nettoyage et standardisation des donnees Bronze -> Silver.
"""
import pandas as pd
import re
import json
from pathlib import Path
from pipeline.utils import normaliser_ville, get_region, normaliser_contrat, normaliser_date, extraire_annee_mois


def charger_depuis_bronze(data_lake_root: str) -> pd.DataFrame:
    """Charge et consolide toutes les offres depuis la zone Bronze."""
    all_offres = []
    bronze_path = Path(data_lake_root) / 'bronze'

    for json_file in bronze_path.rglob('offres_raw.json'):
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        all_offres.extend(data.get('offres', []))

    df = pd.DataFrame(all_offres)
    print(f"[SILVER] {len(df)} offres chargees depuis Bronze")
    return df


def nettoyer_titres_postes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardise les intitules de poste en familles de profils IT.
    Les titres non reconnus sont conserves avec 'Autre IT'.
    """
    mapping_profils = {
        # Data Engineering
        r'data\s*eng(ineer|ineer\w*|\.)?|ingénieur\s+data|dev\s+data\s+eng': 'Data Engineer',
        r'etl\s*dev|pipeline\s*dev|ingénieur\s+etl': 'Data Engineer',
        # Data Analysis
        r'data\s*anal(yst|yste|ytics)|analyste?\s+data|bi\s+anal': 'Data Analyst',
        r'business\s+intel(ligence)?|ingénieur\s+bi|développeur\s+bi': 'Data Analyst',
        r'reporting\s+(anal|spec|officer)': 'Data Analyst',
        # Data Science
        r'data\s*sci(entist|ence)|machine\s*learn|ml\s*eng|ia\s*eng': 'Data Scientist',
        r'deep\s*learn|nlp\s*eng|computer\s*vision': 'Data Scientist',
        # Software Engineering
        r'full\s*stack|fullstack': 'Developpeur Full Stack',
        r'back[\s-]*end|backend': 'Developpeur Backend',
        r'front[\s-]*end|frontend|ui\s+dev': 'Developpeur Frontend',
        r'dev(eloppeur|eloper)?\s+mobile|ios\s+dev|android\s+dev|flutter': 'Developpeur Mobile',
        # Infrastructure
        r'devops|sre|site\s*reliab': 'DevOps / SRE',
        r'cloud\s*(arch|eng|admin)|aws\s+eng|gcp\s+eng|azure\s+eng': 'Cloud Engineer',
        r'sys(admin|tème|teme)|admin.*syst|réseau\s+inf|network\s+eng': 'Admin Systemes & Reseaux',
        # Cyber
        r'cyber|sécurité\s+info|securite|pentester|soc\s+anal': 'Cybersecurite',
        # Management
        r'chef\s+de\s+proj(et)?|project\s+man|scrum\s*master': 'Chef de Projet IT',
        r'architect(e)?\s+(log|tech|data|cloud|sol)': 'Architecte IT',
    }

    df['profil_normalise'] = 'Autre IT'
    df['profil_source'] = df['titre_poste'].str.lower().str.strip()

    for pattern, profil in mapping_profils.items():
        masque = df['profil_source'].str.contains(pattern, regex=True, na=False)
        df.loc[masque & (df['profil_normalise'] == 'Autre IT'), 'profil_normalise'] = profil

    non_classes = (df['profil_normalise'] == 'Autre IT').sum()
    print(f"[SILVER] Titres : {non_classes} offres classees 'Autre IT' sur {len(df)}")
    return df


def normaliser_salaires(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extrait et normalise les salaires en MAD mensuel brut.
    Fourchettes -> min/max/median, K -> *1000, EUR -> MAD (10.8)
    """
    TAUX_EUR_MAD = 10.8

    def parser_salaire(valeur):
        if pd.isna(valeur) or str(valeur).lower().strip() in ['null', 'confidentiel', 'selon profil', '', 'a negocier', 'à négocier']:
            return None, None, False

        s = str(valeur).lower().replace(' ', '').replace('\u202f', '')

        # Conversion EUR -> MAD
        est_eur = 'eur' in s or '€' in s
        s = s.replace('eur', '').replace('€', '').replace('mad', '').replace('dh', '')

        # Gestion "K" (milliers)
        s = re.sub(r'(\d+(?:\.\d+)?)k', lambda m: str(int(float(m.group(1)) * 1000)), s)

        # Extraction des montants
        nombres = re.findall(r'\d+(?:\.\d+)?', s)

        if not nombres:
            return None, None, False

        montants = [float(n) for n in nombres]

        if est_eur:
            montants = [m * TAUX_EUR_MAD for m in montants]

        if len(montants) >= 2:
            sal_min = min(montants[:2])
            sal_max = max(montants[:2])
        else:
            sal_min = sal_max = montants[0]

        # Coherence : salaires IT Maroc entre 3000 et 100000 MAD
        if sal_min < 3000 or sal_max > 100000:
            return None, None, False

        return sal_min, sal_max, True

    resultats = df['salaire_brut'].apply(
        lambda x: pd.Series(parser_salaire(x), index=['salaire_min_mad', 'salaire_max_mad', 'salaire_connu'])
    )
    df = pd.concat([df, resultats], axis=1)
    df['salaire_median_mad'] = df.apply(
        lambda r: (r['salaire_min_mad'] + r['salaire_max_mad']) / 2 if r['salaire_connu'] else None, axis=1
    )

    pct_connu = df['salaire_connu'].mean() * 100
    print(f"[SILVER] Salaires : {pct_connu:.1f}% des offres ont un salaire valide")
    return df


def normaliser_experience(df: pd.DataFrame) -> pd.DataFrame:
    """Transforme l'experience en valeur numerique (annees)."""
    def parser_experience(valeur):
        if pd.isna(valeur):
            return None, None
        s = str(valeur).lower()

        if any(mot in s for mot in ['debutant', 'débutant', 'junior', 'stage', 'sans exp']):
            return 0, 2
        if any(mot in s for mot in ['senior', 'confirmé', 'confirme', 'expert', 'lead']):
            return 5, None

        fourchette = re.search(r'(\d+)\s*[-àa]\s*(\d+)', s)
        if fourchette:
            return int(fourchette.group(1)), int(fourchette.group(2))

        min_seul = re.search(r'(\d+)\s*(?:ans?|years?)', s)
        if min_seul:
            return int(min_seul.group(1)), None

        nombre = re.search(r'(\d+)', s)
        if nombre:
            return int(nombre.group(1)), None

        return None, None

    resultats = df['experience_requise'].apply(
        lambda x: pd.Series(parser_experience(x), index=['experience_min_ans', 'experience_max_ans'])
    )
    df = pd.concat([df, resultats], axis=1)
    return df


def normaliser_villes_contrats(df: pd.DataFrame) -> pd.DataFrame:
    """Normalise les villes et types de contrat."""
    df['ville_std'] = df['ville'].apply(normaliser_ville)
    df['region_admin'] = df['ville_std'].apply(get_region)
    df['type_contrat_std'] = df['type_contrat'].apply(normaliser_contrat)
    return df


def normaliser_dates(df: pd.DataFrame) -> pd.DataFrame:
    """Normalise les dates et extrait annee/mois."""
    df['date_publication'] = df['date_publication'].apply(normaliser_date)
    df['date_expiration'] = df['date_expiration'].apply(normaliser_date)

    # Extraire annee et mois
    df['annee'] = df['date_publication'].apply(lambda x: extraire_annee_mois(x)[0])
    df['mois'] = df['date_publication'].apply(lambda x: extraire_annee_mois(x)[1])

    # Flag dates incoherentes (publication > expiration)
    df['date_coherente'] = True
    mask = df['date_publication'].notna() & df['date_expiration'].notna()
    df.loc[mask, 'date_coherente'] = df.loc[mask, 'date_publication'] <= df.loc[mask, 'date_expiration']

    incoherentes = (~df['date_coherente']).sum()
    print(f"[SILVER] Dates : {incoherentes} dates incoherentes detectees")
    return df


def transformer_silver(data_lake_root: str) -> pd.DataFrame:
    """Pipeline complet Bronze -> Silver pour les offres."""
    print("=" * 60)
    print("[SILVER] Debut de la transformation Bronze -> Silver")
    print("=" * 60)

    # Charger depuis Bronze
    df = charger_depuis_bronze(data_lake_root)
    nb_initial = len(df)
    print(f"[SILVER] Lignes initiales : {nb_initial}")

    # Appliquer les transformations
    df = nettoyer_titres_postes(df)
    df = normaliser_salaires(df)
    df = normaliser_experience(df)
    df = normaliser_villes_contrats(df)
    df = normaliser_dates(df)

    # Supprimer les doublons par id_offre
    nb_avant_dedup = len(df)
    df = df.drop_duplicates(subset='id_offre', keep='first')
    doublons = nb_avant_dedup - len(df)
    print(f"[SILVER] Doublons supprimes : {doublons}")
    print(f"[SILVER] Lignes finales : {len(df)}")

    print("=" * 60)
    print("[SILVER] Transformation terminee")
    print("=" * 60)
    return df
