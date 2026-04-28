"""
Bronze Ingestion Pipeline
Charge les donnees brutes dans la zone Bronze sans aucune modification.
Partitionne par source et par mois de publication.
"""
import json
import os
from datetime import datetime
from pathlib import Path
import re


def ingerer_bronze(filepath_source: str, data_lake_root: str) -> dict:
    """
    Charge les donnees brutes dans la zone Bronze sans modification.
    Partitionne par source et par mois de publication.

    Principe fondamental : la zone Bronze est IMMUABLE.
    On ne modifie JAMAIS les donnees une fois chargees en Bronze.
    """
    with open(filepath_source, 'r', encoding='utf-8') as f:
        data = json.load(f)

    offres = data.get('offres', [])
    stats = {'total': len(offres), 'par_source': {}, 'par_mois': {}, 'nb_fichiers': 0}

    # Partitionnement par source et par mois
    partitions = {}
    for offre in offres:
        source = offre.get('source', 'inconnu').lower().replace(' ', '_')
        date_pub = offre.get('date_publication', '')

        # Gerer les formats de date differents
        mois_partition = 'date_inconnue'
        try:
            s = str(date_pub).strip()
            # Format DD/MM/YYYY
            m = re.match(r'^(\d{2})/(\d{2})/(\d{4})$', s)
            if m:
                mois_partition = f"{m.group(3)}_{m.group(2)}"
            else:
                # Format YYYY-MM-DD
                mois_partition = datetime.strptime(s[:7], '%Y-%m').strftime('%Y_%m')
        except (ValueError, TypeError):
            mois_partition = 'date_inconnue'

        cle = f"{source}/{mois_partition}"
        if cle not in partitions:
            partitions[cle] = []
        partitions[cle].append(offre)

    # Ecriture dans Bronze
    nb_fichiers = 0
    for partition, offres_partition in partitions.items():
        chemin_dir = os.path.join(data_lake_root, 'bronze', partition)
        os.makedirs(chemin_dir, exist_ok=True)

        chemin_fichier = os.path.join(chemin_dir, 'offres_raw.json')
        with open(chemin_fichier, 'w', encoding='utf-8') as f:
            json.dump({
                'metadata': {
                    'source_fichier': filepath_source,
                    'date_ingestion': datetime.now().isoformat(),
                    'partition': partition,
                    'nb_offres': len(offres_partition)
                },
                'offres': offres_partition
            }, f, ensure_ascii=False, indent=2)

        nb_fichiers += 1
        source_nom = partition.split('/')[0]
        stats['par_source'][source_nom] = stats['par_source'].get(source_nom, 0) + len(offres_partition)
        mois_nom = partition.split('/')[1]
        stats['par_mois'][mois_nom] = stats['par_mois'].get(mois_nom, 0) + len(offres_partition)

    stats['nb_fichiers'] = nb_fichiers
    print(f"[BRONZE] {stats['total']} offres ingerees dans {nb_fichiers} partitions")
    for src, count in sorted(stats['par_source'].items()):
        print(f"  - {src}: {count} offres")
    return stats


if __name__ == "__main__":
    import sys
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    src = os.path.join(root, "data", "raw", "offres_emploi_it_maroc.json")
    lake = os.path.join(root, "data_lake")
    stats = ingerer_bronze(src, lake)
    print(f"\n[BRONZE] Terminee. {stats['nb_fichiers']} fichiers crees.")
