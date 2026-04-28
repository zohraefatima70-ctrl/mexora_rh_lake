"""
Mexora RH Intelligence - Orchestration du pipeline Data Lake.
Execute les etapes Bronze -> Silver -> Gold.
"""
import os
import sys
import time

# Ajouter le repertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pipeline.bronze_ingestion import ingerer_bronze
from pipeline.silver_transform import transformer_silver
from pipeline.silver_nlp import extraire_competences, sauvegarder_silver
from pipeline.gold_aggregation import construire_gold


def main():
    """Point d'entree principal du pipeline."""
    root = os.path.dirname(os.path.abspath(__file__))
    data_lake_root = os.path.join(root, "data_lake")
    source_file = os.path.join(root, "data", "raw", "offres_emploi_it_maroc.json")
    referentiel_file = os.path.join(root, "data", "raw", "referentiel_competences_it.json")

    print("=" * 70)
    print("  MEXORA RH INTELLIGENCE - Pipeline Data Lake")
    print("=" * 70)
    t0 = time.time()

    # --- ETAPE 1 : Bronze ---
    print("\n>>> ETAPE 1 : Ingestion Bronze")
    stats_bronze = ingerer_bronze(source_file, data_lake_root)

    # --- ETAPE 2 : Silver (nettoyage) ---
    print("\n>>> ETAPE 2 : Transformation Silver (nettoyage)")
    df_offres = transformer_silver(data_lake_root)

    # --- ETAPE 3 : Silver (NLP - extraction competences) ---
    print("\n>>> ETAPE 3 : Extraction competences (NLP)")
    df_competences = extraire_competences(df_offres, referentiel_file)

    # Sauvegarder Silver
    sauvegarder_silver(df_offres, df_competences, data_lake_root)

    # --- ETAPE 4 : Gold (agregats) ---
    print("\n>>> ETAPE 4 : Construction tables Gold")
    construire_gold(data_lake_root)

    elapsed = time.time() - t0
    print("\n" + "=" * 70)
    print(f"  Pipeline termine en {elapsed:.1f} secondes")
    print(f"  Bronze : {stats_bronze['total']} offres -> {stats_bronze['nb_fichiers']} fichiers")
    print(f"  Silver : {len(df_offres)} offres nettoyees, {len(df_competences)} lignes competences")
    print(f"  Gold   : 5 tables analytiques")
    print("=" * 70)


if __name__ == "__main__":
    main()
