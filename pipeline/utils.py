"""
Fonctions utilitaires partagees par les pipelines.
"""
import re
import os
from pathlib import Path


# Mapping de normalisation des villes marocaines
VILLES_MAPPING = {
    "casablanca": "Casablanca", "casa": "Casablanca", "CASABLANCA": "Casablanca",
    "casablanca ": "Casablanca",
    "rabat": "Rabat", "RABAT": "Rabat", "rabat-sale": "Rabat", "rabat sale": "Rabat",
    "rabat-salé": "Rabat",
    "tanger": "Tanger", "TANGER": "Tanger", "tanger-tétouan": "Tanger", "tangier": "Tanger",
    "marrakech": "Marrakech", "MARRAKECH": "Marrakech", "marrakesh": "Marrakech",
    "fès": "Fes", "fes": "Fes", "FES": "Fes", "fez": "Fes",
    "agadir": "Agadir", "AGADIR": "Agadir",
    "oujda": "Oujda",
    "meknès": "Meknes", "meknes": "Meknes", "MEKNES": "Meknes",
    "kénitra": "Kenitra", "kenitra": "Kenitra",
    "tétouan": "Tetouan", "tetouan": "Tetouan",
}

# Mapping ville -> region administrative
REGIONS_MAPPING = {
    "Casablanca": "Casablanca-Settat",
    "Rabat": "Rabat-Sale-Kenitra",
    "Tanger": "Tanger-Tetouan-Al Hoceima",
    "Marrakech": "Marrakech-Safi",
    "Fes": "Fes-Meknes",
    "Agadir": "Souss-Massa",
    "Oujda": "Oriental",
    "Meknes": "Fes-Meknes",
    "Kenitra": "Rabat-Sale-Kenitra",
    "Tetouan": "Tanger-Tetouan-Al Hoceima",
}

# Mapping de normalisation des types de contrat
CONTRAT_MAPPING = {
    "cdi": "CDI", "contrat à durée indéterminée": "CDI", "permanent": "CDI", "cdi ": "CDI",
    "cdd": "CDD", "contrat à durée déterminée": "CDD",
    "freelance": "Freelance", "mission": "Freelance", "indépendant": "Freelance",
    "stage": "Stage", "stage pfe": "Stage", "internship": "Stage",
}


def normaliser_ville(ville_brute):
    """Normalise le nom d'une ville marocaine."""
    if not ville_brute or str(ville_brute).lower().strip() in ['nan', 'none', '']:
        return "Inconnue"
    cle = str(ville_brute).lower().strip()
    return VILLES_MAPPING.get(cle, ville_brute.strip().title())


def get_region(ville_std):
    """Retourne la region administrative pour une ville."""
    return REGIONS_MAPPING.get(ville_std, "Autre")


def normaliser_contrat(contrat_brut):
    """Normalise le type de contrat."""
    if not contrat_brut or str(contrat_brut).lower().strip() in ['nan', 'none', '']:
        return "Non precise"
    cle = str(contrat_brut).lower().strip()
    return CONTRAT_MAPPING.get(cle, contrat_brut.strip())


def normaliser_date(date_str):
    """Normalise une date au format YYYY-MM-DD."""
    if not date_str or str(date_str).lower().strip() in ['nan', 'none', '']:
        return None
    s = str(date_str).strip()
    # Format DD/MM/YYYY
    m = re.match(r'^(\d{2})/(\d{2})/(\d{4})$', s)
    if m:
        return f"{m.group(3)}-{m.group(2)}-{m.group(1)}"
    # Format YYYY-MM-DD (deja bon)
    m = re.match(r'^\d{4}-\d{2}-\d{2}$', s)
    if m:
        return s
    return None


def extraire_annee_mois(date_str):
    """Extrait annee et mois d'une date normalisee."""
    if not date_str:
        return None, None
    try:
        parts = str(date_str)[:7].split('-')
        return parts[0], parts[1]
    except (IndexError, ValueError):
        return None, None


def ensure_dir(path):
    """Cree un repertoire s'il n'existe pas."""
    Path(path).mkdir(parents=True, exist_ok=True)
    return path
