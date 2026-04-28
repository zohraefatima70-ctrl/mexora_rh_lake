"""
Analyse du marche de l'emploi IT au Maroc - Requetes DuckDB
Mexora RH Intelligence
"""
import duckdb
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
GOLD = os.path.join(ROOT, "..", "data_lake", "gold")
SILVER = os.path.join(ROOT, "..", "data_lake", "silver")
OUT = os.path.join(ROOT, "output")
os.makedirs(OUT, exist_ok=True)

GOLD_TOP_COMP   = f"{GOLD}/top_competences.parquet"
GOLD_SALAIRES   = f"{GOLD}/salaires_par_profil.parquet"
GOLD_VILLES     = f"{GOLD}/offres_par_ville.parquet"
GOLD_ENTREPRISES= f"{GOLD}/entreprises_recruteurs.parquet"
GOLD_TENDANCES  = f"{GOLD}/tendances_mensuelles.parquet"
SILVER_OFFRES   = f"{SILVER}/offres_clean/offres_clean.parquet"

COLORS = {
    'langages': '#4361EE', 'frameworks_web': '#3A0CA3', 'data_engineering': '#F72585',
    'cloud': '#7209B7', 'bi_analytics': '#560BAD', 'devops_infra': '#480CA8',
    'databases': '#3F37C9', 'data_science_ml': '#4CC9F0', 'methodologies': '#4895EF',
    'securite': '#B5179E', 'autres': '#F3722C',
}
PROFIL_COLORS = {
    'Data Engineer': '#F72585', 'Data Analyst': '#4361EE', 'Data Scientist': '#7209B7',
    'Developpeur Full Stack': '#4CC9F0', 'Developpeur Backend': '#3A0CA3',
    'Developpeur Frontend': '#4895EF', 'DevOps / SRE': '#F3722C',
    'Cloud Engineer': '#560BAD', 'Developpeur Mobile': '#3F37C9',
    'Cybersecurite': '#B5179E', 'Chef de Projet IT': '#023E8A', 'Autre IT': '#888',
}

con = duckdb.connect()

# ── Q1 : Top competences ──────────────────────────────────────────────────
def q1_top_competences():
    print("\n" + "="*60)
    print("Q1 - Top competences IT au Maroc")
    print("="*60)

    df_top20 = con.execute(f"""
        SELECT famille, competence, SUM(nb_offres_mentionnent) AS nb_offres, ROUND(AVG(pct_offres_total),2) AS pct
        FROM '{GOLD_TOP_COMP}'
        WHERE competence != 'non_detecte'
        GROUP BY famille, competence
        ORDER BY nb_offres DESC
        LIMIT 20
    """).df()
    print("\nTop 20 competences (toutes offres):")
    print(df_top20.to_string(index=False))

    df_data = con.execute(f"""
        SELECT profil, famille, competence, nb_offres_mentionnent, rang_dans_profil
        FROM '{GOLD_TOP_COMP}'
        WHERE profil IN ('Data Engineer','Data Analyst','Data Scientist')
          AND rang_dans_profil <= 5
        ORDER BY profil, rang_dans_profil
    """).df()
    print("\nTop 5 competences par profil data:")
    print(df_data.to_string(index=False))

    # Graphique
    fig, axes = plt.subplots(1, 2, figsize=(18, 8))
    fig.suptitle("Q1 - Competences IT les plus demandees au Maroc", fontsize=15, fontweight='bold')

    # Barres Top 20
    ax = axes[0]
    bar_colors = [COLORS.get(f, '#888') for f in df_top20['famille']]
    bars = ax.barh(df_top20['competence'][::-1], df_top20['nb_offres'][::-1], color=bar_colors[::-1])
    ax.set_xlabel("Nombre d'offres")
    ax.set_title("Top 20 competences (toutes offres)")
    for bar, v in zip(bars, df_top20['nb_offres'][::-1]):
        ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2, str(v), va='center', fontsize=8)

    # Grouped bar profils data
    ax2 = axes[1]
    profils = ['Data Engineer', 'Data Analyst', 'Data Scientist']
    palette = [PROFIL_COLORS[p] for p in profils]
    for i, profil in enumerate(profils):
        sub = df_data[df_data['profil'] == profil].head(5)
        y = range(i*6, i*6+len(sub))
        ax2.barh(list(y), sub['nb_offres_mentionnent'], color=palette[i], label=profil)
        for j, (_, row) in enumerate(sub.iterrows()):
            ax2.text(row['nb_offres_mentionnent']+0.5, i*6+j, row['competence'], va='center', fontsize=8)
    ax2.set_xlabel("Nb offres")
    ax2.set_title("Top 5 competences par profil data")
    ax2.legend()
    ax2.set_yticks([])

    plt.tight_layout()
    plt.savefig(os.path.join(OUT, "q1_top_competences.png"), dpi=150, bbox_inches='tight')
    plt.close()
    print("[OK] Graphique sauvegarde: q1_top_competences.png")
    return df_top20, df_data


# ── Q2 : Villes ───────────────────────────────────────────────────────────
def q2_villes():
    print("\n" + "="*60)
    print("Q2 - Tanger vs Casablanca vs Rabat")
    print("="*60)

    df_villes = con.execute(f"""
        SELECT ville, profil, SUM(nb_offres) AS nb_offres,
               SUM(nb_offres_remote) AS nb_remote,
               ROUND(SUM(nb_offres_remote)*100.0/NULLIF(SUM(nb_offres),0),1) AS pct_remote,
               RANK() OVER (PARTITION BY profil ORDER BY SUM(nb_offres) DESC) AS rang_ville
        FROM '{GOLD_VILLES}'
        WHERE ville IN ('Casablanca','Rabat','Tanger','Marrakech','Fes')
        GROUP BY ville, profil
        ORDER BY profil, rang_ville
    """).df()
    print(df_villes.head(25).to_string(index=False))

    df_global = con.execute(f"""
        SELECT ville, SUM(nb_offres) AS total_offres,
               ROUND(SUM(nb_offres_remote)*100.0/NULLIF(SUM(nb_offres),0),1) AS pct_remote
        FROM '{GOLD_VILLES}'
        GROUP BY ville ORDER BY total_offres DESC LIMIT 8
    """).df()
    print("\nTotal offres par ville:")
    print(df_global.to_string(index=False))

    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    fig.suptitle("Q2 - Repartition geographique du marche IT", fontsize=14, fontweight='bold')

    # Barres par ville
    ax = axes[0]
    colors_v = ['#F72585','#4361EE','#7209B7','#F3722C','#4CC9F0','#3A0CA3','#560BAD','#4895EF']
    bars = ax.bar(df_global['ville'], df_global['total_offres'], color=colors_v[:len(df_global)])
    ax.set_title("Volume total d'offres IT par ville")
    ax.set_xlabel("Ville")
    ax.set_ylabel("Nombre d'offres")
    ax.tick_params(axis='x', rotation=30)
    for bar, v in zip(bars, df_global['total_offres']):
        ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+5, str(v), ha='center', fontsize=8)

    # % remote
    ax2 = axes[1]
    colors_r = ['#F72585' if v=='Tanger' else '#4361EE' for v in df_global['ville']]
    bars2 = ax2.bar(df_global['ville'], df_global['pct_remote'], color=colors_r)
    ax2.set_title("% offres Remote/Hybride par ville")
    ax2.set_xlabel("Ville")
    ax2.set_ylabel("% remote")
    ax2.tick_params(axis='x', rotation=30)
    for bar, v in zip(bars2, df_global['pct_remote']):
        ax2.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.3, f"{v}%", ha='center', fontsize=8)

    plt.tight_layout()
    plt.savefig(os.path.join(OUT, "q2_villes.png"), dpi=150, bbox_inches='tight')
    plt.close()
    print("[OK] Graphique sauvegarde: q2_villes.png")
    return df_global


# ── Q3 : Salaires ─────────────────────────────────────────────────────────
def q3_salaires():
    print("\n" + "="*60)
    print("Q3 - Salaires mediants par profil IT")
    print("="*60)

    df_sal = con.execute(f"""
        SELECT profil, SUM(nb_offres) AS nb_offres_total,
               SUM(nb_offres_avec_salaire) AS nb_avec_salaire,
               ROUND(SUM(nb_offres_avec_salaire)*100.0/NULLIF(SUM(nb_offres),0),1) AS pct_salaire,
               ROUND(MEDIAN(salaire_median_mad),0) AS salaire_median,
               ROUND(MIN(salaire_min_observe),0) AS plancher,
               ROUND(MAX(salaire_max_observe),0) AS plafond
        FROM '{GOLD_SALAIRES}'
        GROUP BY profil ORDER BY salaire_median DESC NULLS LAST
    """).df()
    print(df_sal.to_string(index=False))

    df_tanger = con.execute(f"""
        SELECT profil, nb_offres, salaire_median_mad, salaire_q1_mad, salaire_q3_mad
        FROM '{GOLD_SALAIRES}'
        WHERE ville='Tanger' AND nb_offres>=3
        ORDER BY salaire_median_mad DESC NULLS LAST
    """).df()
    print("\nSalaires a Tanger:")
    print(df_tanger.to_string(index=False))

    # Boxplot
    df_box = con.execute(f"""
        SELECT profil_normalise AS profil, salaire_median_mad
        FROM '{SILVER_OFFRES}'
        WHERE salaire_connu=true AND salaire_median_mad IS NOT NULL
          AND profil_normalise IN ('Data Engineer','Data Analyst','Data Scientist',
              'Developpeur Full Stack','DevOps / SRE','Cloud Engineer')
    """).df()

    fig, ax = plt.subplots(figsize=(14, 7))
    profils_ord = df_box.groupby('profil')['salaire_median_mad'].median().sort_values(ascending=False).index.tolist()
    data_plot = [df_box[df_box['profil']==p]['salaire_median_mad'].dropna().values for p in profils_ord]
    bp = ax.boxplot(data_plot, labels=[p.replace('Developpeur ','Dev.') for p in profils_ord],
                    patch_artist=True, notch=False)
    colors_bp = [PROFIL_COLORS.get(p, '#888') for p in profils_ord]
    for patch, c in zip(bp['boxes'], colors_bp):
        patch.set_facecolor(c)
        patch.set_alpha(0.7)
    ax.set_title("Distribution des salaires par profil IT (MAD/mois)", fontsize=13, fontweight='bold')
    ax.set_ylabel("Salaire MAD/mois")
    ax.set_xlabel("Profil")
    ax.tick_params(axis='x', rotation=20)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{int(x):,}"))
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, "q3_salaires_boxplot.png"), dpi=150, bbox_inches='tight')
    plt.close()
    print("[OK] Graphique sauvegarde: q3_salaires_boxplot.png")
    return df_sal


# ── Q4 : Experience vs Salaire ────────────────────────────────────────────
def q4_experience_salaire():
    print("\n" + "="*60)
    print("Q4 - Correlation Experience / Salaire")
    print("="*60)

    df_exp = con.execute(f"""
        SELECT profil_normalise AS profil,
            CASE
                WHEN experience_min_ans=0 THEN '0-Debutant'
                WHEN experience_min_ans BETWEEN 1 AND 2 THEN '1-2 ans'
                WHEN experience_min_ans BETWEEN 3 AND 4 THEN '3-4 ans'
                WHEN experience_min_ans BETWEEN 5 AND 7 THEN '5-7 ans'
                WHEN experience_min_ans>=8 THEN '8+ ans'
                ELSE 'Non precise'
            END AS tranche_exp,
            COUNT(*) AS nb_offres,
            ROUND(MEDIAN(salaire_median_mad) FILTER (WHERE salaire_connu=true),0) AS salaire_median
        FROM '{SILVER_OFFRES}'
        WHERE profil_normalise IN ('Data Engineer','Data Analyst','Data Scientist')
        GROUP BY profil_normalise, tranche_exp
        ORDER BY profil_normalise, tranche_exp
    """).df()
    print(df_exp.to_string(index=False))

    df_corr = con.execute(f"""
        SELECT profil_normalise AS profil,
               ROUND(CORR(CAST(experience_min_ans AS DOUBLE),
                          CAST(salaire_median_mad AS DOUBLE)),3) AS correlation_pearson
        FROM '{SILVER_OFFRES}'
        WHERE salaire_connu=true AND experience_min_ans IS NOT NULL
          AND salaire_median_mad IS NOT NULL
        GROUP BY profil_normalise
        ORDER BY correlation_pearson DESC NULLS LAST
    """).df()
    print("\nCorrelation Pearson experience/salaire par profil:")
    print(df_corr.to_string(index=False))

    fig, ax = plt.subplots(figsize=(12, 6))
    tranches = ['0-Debutant','1-2 ans','3-4 ans','5-7 ans','8+ ans']
    profils_data = ['Data Engineer','Data Analyst','Data Scientist']
    x = range(len(tranches))
    width = 0.28
    for i, profil in enumerate(profils_data):
        sub = df_exp[df_exp['profil']==profil].set_index('tranche_exp')
        vals = [sub.loc[t,'salaire_median'] if t in sub.index else 0 for t in tranches]
        offset = (i - 1) * width
        bars = ax.bar([xi + offset for xi in x], vals, width,
                      label=profil, color=PROFIL_COLORS.get(profil,'#888'), alpha=0.85)
    ax.set_xticks(list(x))
    ax.set_xticklabels(tranches)
    ax.set_ylabel("Salaire median (MAD)")
    ax.set_title("Q4 - Salaire median par tranche d'experience (profils data)", fontsize=13, fontweight='bold')
    ax.legend()
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{int(v):,}"))
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, "q4_experience_salaire.png"), dpi=150, bbox_inches='tight')
    plt.close()
    print("[OK] Graphique sauvegarde: q4_experience_salaire.png")
    return df_corr


# ── Q5 : Entreprises ──────────────────────────────────────────────────────
def q5_entreprises():
    print("\n" + "="*60)
    print("Q5 - Top entreprises recruteurs")
    print("="*60)

    df_top = con.execute(f"""
        SELECT entreprise, ville, nb_offres_publiees, nb_profils_differents,
               salaire_moyen_propose,
               RANK() OVER (ORDER BY nb_offres_publiees DESC) AS rang
        FROM '{GOLD_ENTREPRISES}'
        ORDER BY nb_offres_publiees DESC LIMIT 20
    """).df()
    print(df_top.to_string(index=False))

    df_tanger = con.execute(f"""
        SELECT entreprise, nb_offres_publiees, salaire_moyen_propose,
            CASE
                WHEN salaire_moyen_propose>20000 THEN 'Fort'
                WHEN salaire_moyen_propose>12000 THEN 'Moyen'
                ELSE 'Faible'
            END AS niveau_competition
        FROM '{GOLD_ENTREPRISES}'
        WHERE ville='Tanger'
        ORDER BY salaire_moyen_propose DESC NULLS LAST
    """).df()
    print("\nConcurrents Mexora a Tanger:")
    print(df_tanger.to_string(index=False))

    fig, ax = plt.subplots(figsize=(14, 8))
    top15 = df_top.head(15)
    colors_e = ['#F72585' if v=='Tanger' else '#4361EE' for v in top15['ville']]
    bars = ax.barh(top15['entreprise'][::-1], top15['nb_offres_publiees'][::-1], color=colors_e[::-1])
    ax.set_xlabel("Nombre d'offres publiees")
    ax.set_title("Q5 - Top 15 entreprises recruteurs IT au Maroc\n(rouge = Tanger)", fontsize=13, fontweight='bold')
    for bar, v in zip(bars, top15['nb_offres_publiees'][::-1]):
        ax.text(bar.get_width()+0.1, bar.get_y()+bar.get_height()/2, str(v), va='center', fontsize=9)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, "q5_entreprises.png"), dpi=150, bbox_inches='tight')
    plt.close()
    print("[OK] Graphique sauvegarde: q5_entreprises.png")
    return df_top


# ── Dashboard final 4 visualisations ──────────────────────────────────────
def dashboard_final():
    print("\n[DASHBOARD] Generation du dashboard de synthese...")

    df_comp = con.execute(f"""
        SELECT famille, competence, SUM(nb_offres_mentionnent) AS nb
        FROM '{GOLD_TOP_COMP}' WHERE competence!='non_detecte'
        GROUP BY famille, competence ORDER BY nb DESC LIMIT 15
    """).df()

    df_tendances = con.execute(f"""
        SELECT annee||'-'||mois AS periode, profil, SUM(nb_offres) AS nb
        FROM '{GOLD_TENDANCES}'
        WHERE profil IN ('Data Engineer','Data Analyst','Data Scientist')
          AND annee IS NOT NULL
        GROUP BY annee, mois, profil ORDER BY annee, mois
    """).df()

    df_villes_map = con.execute(f"""
        SELECT ville, SUM(nb_offres) AS nb FROM '{GOLD_VILLES}'
        GROUP BY ville ORDER BY nb DESC LIMIT 10
    """).df()

    df_box2 = con.execute(f"""
        SELECT profil_normalise AS profil, salaire_median_mad
        FROM '{SILVER_OFFRES}'
        WHERE salaire_connu=true AND salaire_median_mad IS NOT NULL
          AND profil_normalise IN ('Data Engineer','Data Analyst','Data Scientist',
              'Developpeur Full Stack','DevOps / SRE')
    """).df()

    fig = plt.figure(figsize=(20, 14))
    fig.suptitle("Dashboard - Marche de l'Emploi IT au Maroc | Mexora RH Intelligence 2024",
                 fontsize=16, fontweight='bold', y=0.98)

    # 1. Carte (bubble chart)
    ax1 = fig.add_subplot(2, 2, 1)
    ville_coords = {
        'Casablanca': (0.35, 0.35), 'Rabat': (0.32, 0.55), 'Tanger': (0.25, 0.78),
        'Marrakech': (0.30, 0.20), 'Fes': (0.52, 0.60), 'Agadir': (0.18, 0.12),
        'Oujda': (0.78, 0.55), 'Meknes': (0.44, 0.58), 'Kenitra': (0.30, 0.60),
        'Tetouan': (0.28, 0.82),
    }
    for _, row in df_villes_map.iterrows():
        v = row['ville']
        if v in ville_coords:
            x, y = ville_coords[v]
            size = max(100, row['nb'] * 0.4)
            c = '#F72585' if v == 'Tanger' else '#4361EE'
            ax1.scatter(x, y, s=size, color=c, alpha=0.7)
            ax1.annotate(f"{v}\n({row['nb']})", (x, y), textcoords="offset points",
                        xytext=(5, 5), fontsize=7)
    ax1.set_xlim(0, 1); ax1.set_ylim(0, 1)
    ax1.set_title("Volume d'offres IT par ville (taille = nb offres)", fontweight='bold')
    ax1.axis('off')
    ax1.add_patch(plt.Rectangle((0, 0), 1, 1, fill=False, edgecolor='#ccc'))

    # 2. Top 15 competences
    ax2 = fig.add_subplot(2, 2, 2)
    bar_colors2 = [COLORS.get(f, '#888') for f in df_comp['famille']]
    ax2.barh(df_comp['competence'][::-1], df_comp['nb'][::-1], color=bar_colors2[::-1])
    ax2.set_title("Top 15 competences IT (par famille)", fontweight='bold')
    ax2.set_xlabel("Nb offres")

    # 3. Boxplot salaires
    ax3 = fig.add_subplot(2, 2, 3)
    profils_ord2 = df_box2.groupby('profil')['salaire_median_mad'].median().sort_values(ascending=False).index.tolist()
    data_bp = [df_box2[df_box2['profil']==p]['salaire_median_mad'].dropna().values for p in profils_ord2]
    bp2 = ax3.boxplot(data_bp, labels=[p.replace('Developpeur ','Dev.') for p in profils_ord2],
                      patch_artist=True)
    for patch, p in zip(bp2['boxes'], profils_ord2):
        patch.set_facecolor(PROFIL_COLORS.get(p, '#888'))
        patch.set_alpha(0.7)
    ax3.set_title("Distribution salaires par profil (MAD/mois)", fontweight='bold')
    ax3.set_ylabel("MAD/mois")
    ax3.tick_params(axis='x', rotation=20)
    ax3.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{int(v):,}"))

    # 4. Tendances mensuelles
    ax4 = fig.add_subplot(2, 2, 4)
    for profil, grp in df_tendances.groupby('profil'):
        ax4.plot(range(len(grp)), grp['nb'], marker='o', markersize=3,
                 label=profil, color=PROFIL_COLORS.get(profil,'#888'), linewidth=2)
    periodes = df_tendances['periode'].unique()
    step = max(1, len(periodes)//8)
    ax4.set_xticks(range(0, len(periodes), step))
    ax4.set_xticklabels(list(periodes)[::step], rotation=30, fontsize=7)
    ax4.set_title("Evolution mensuelle des offres data (2023-2024)", fontweight='bold')
    ax4.set_ylabel("Nb offres")
    ax4.legend(fontsize=8)
    ax4.grid(alpha=0.3)

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig(os.path.join(OUT, "dashboard_synthese.png"), dpi=150, bbox_inches='tight')
    plt.close()
    print("[OK] Dashboard sauvegarde: dashboard_synthese.png")


if __name__ == "__main__":
    df_top20, df_data = q1_top_competences()
    df_villes = q2_villes()
    df_sal = q3_salaires()
    df_corr = q4_experience_salaire()
    df_ent = q5_entreprises()
    dashboard_final()
    print("\n[OK] Toutes les analyses terminees. Resultats dans analysis/output/")
