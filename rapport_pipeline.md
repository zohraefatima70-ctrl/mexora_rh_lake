# Rapport de Traitement — Pipeline Data Lake Mexora RH Intelligence

**Projet :** Mexora RH Intelligence — Marché IT Marocain  
**Pipeline :** Bronze → Silver → Gold  
**Données :** 5 000 offres d'emploi IT synthétiques (Jan 2023 – Nov 2024)  
**Durée d'exécution :** ~15 secondes (machine locale)

---

## Résumé Exécutif

| Étape | Entrée | Sortie | Taux de rétention |
|-------|--------|--------|-------------------|
| Bronze Ingestion | 5 000 offres (JSON source) | 5 000 offres → 69 fichiers partitionnés | 100% |
| Silver Transform | 5 000 offres brutes | 5 000 offres nettoyées (après déduplication) | ~100% |
| Silver NLP | 5 000 offres Silver | ~26 711 lignes compétences | N/A (expansion) |
| Gold Aggregation | 2 fichiers Parquet Silver | 5 tables analytiques Parquet | N/A (agrégation) |

---

## ÉTAPE 1 — Bronze Ingestion (`bronze_ingestion.py`)

### Objectif
Charger les données brutes dans la zone Bronze **sans aucune modification**. Principe fondamental : la zone Bronze est immuable (Source of Truth).

---

### T1.1 — Lecture du fichier source

| Paramètre | Valeur |
|-----------|--------|
| **Fichier source** | `data/raw/offres_emploi_it_maroc.json` |
| **Lignes avant** | 1 fichier JSON avec clé `offres` |
| **Lignes après** | 5 000 objets offres chargés en mémoire |
| **Format** | JSON (encodage UTF-8) |

**Règle appliquée :** Lecture directe via `json.load()`, aucune transformation.

**Cas limites :**
- Fichier absent → `FileNotFoundError` non capturée intentionnellement (échec rapide)
- Clé `offres` manquante → `.get('offres', [])` retourne liste vide (0 offres traitées)

---

### T1.2 — Partitionnement par Source et par Mois

| Paramètre | Valeur |
|-----------|--------|
| **Lignes avant** | 5 000 offres |
| **Fichiers créés** | 69 fichiers `offres_raw.json` |
| **Partitions** | `bronze/{source}/{YYYY_MM}/offres_raw.json` |

**Règle appliquée :**
- Extraction du champ `source` → normalisé en minuscules, espaces → `_`
- Extraction du champ `date_publication` → format `YYYY_MM`
- Clé de partition = `{source}/{YYYY_MM}`

**Répartition par source :**
| Source | Offres | Poids théorique |
|--------|--------|-----------------|
| rekrute | ~2 250 | 45% |
| linkedin | ~1 500 | 30% |
| marocannonce | ~1 250 | 25% |

**Répartition temporelle :** 23 mois (Jan 2023 → Nov 2024) × 3 sources = jusqu'à 69 partitions.

**Cas limites rencontrés :**

| Cas limite | Occurrence | Traitement |
|------------|------------|------------|
| `source` absent ou `null` | Possible | → partition `inconnu/...` |
| `date_publication` au format `DD/MM/YYYY` | ~10% des offres | → regex `(\d{2})/(\d{2})/(\d{4})` → `YYYY_MM` |
| `date_publication` au format `YYYY-MM-DD` | ~90% des offres | → `datetime.strptime(s[:7], '%Y-%m')` |
| Date invalide / malformée | Possible | → partition `date_inconnue` (pas de rejet) |
| Valeur `None` pour la date | ~0% | → `mois_partition = 'date_inconnue'` |

**Contenu de chaque fichier Bronze :**
```json
{
  "metadata": {
    "source_fichier": "...",
    "date_ingestion": "2024-11-15T10:23:45.123",
    "partition": "rekrute/2023_06",
    "nb_offres": 72
  },
  "offres": [...]
}
```

---

## ÉTAPE 2 — Silver Transform (`silver_transform.py`)

### Objectif
Nettoyer, standardiser et dédupliquer les données Bronze pour produire un dataset analytique de qualité.

**Lignes initiales (chargées depuis Bronze) : 5 000**

---

### T2.1 — Chargement consolidé depuis Bronze

| Paramètre | Valeur |
|-----------|--------|
| **Lignes avant** | 69 fichiers JSON partitionnés |
| **Lignes après** | 5 000 offres dans un DataFrame pandas unique |

**Règle appliquée :** Parcours récursif de `data_lake/bronze/` via `Path.rglob('offres_raw.json')`, concaténation de toutes les listes `offres`.

**Cas limites :**
- Fichier Bronze corrompu → `json.JSONDecodeError` non capturée (échec rapide voulu)
- Offre sans clé `id_offre` → champ `None` dans le DataFrame (géré à la déduplication)

---

### T2.2 — Normalisation des Titres de Postes (`nettoyer_titres_postes`)

| Paramètre | Valeur |
|-----------|--------|
| **Lignes avant** | 5 000 offres |
| **Lignes après** | 5 000 offres (pas de suppression) |
| **Colonne créée** | `profil_normalise` |

**Règle appliquée :** Mapping regex (17 patterns) sur `titre_poste.lower()` → 13 familles de profils IT normalisées.

**Familles de profils détectées :**
| Profil normalisé | Pattern regex clé |
|-----------------|-------------------|
| Data Engineer | `data\s*eng`, `etl\s*dev`, `pipeline\s*dev` |
| Data Analyst | `data\s*anal`, `bi\s*anal`, `reporting\s*anal` |
| Data Scientist | `data\s*sci`, `machine\s*learn`, `nlp\s*eng` |
| Developpeur Full Stack | `full\s*stack`, `fullstack` |
| Developpeur Backend | `back[\s-]*end`, `backend` |
| Developpeur Frontend | `front[\s-]*end`, `ui\s+dev` |
| Developpeur Mobile | `mobile`, `flutter`, `ios\s+dev` |
| DevOps / SRE | `devops`, `sre`, `site\s*reliab` |
| Cloud Engineer | `cloud\s*(arch\|eng\|admin)` |
| Cybersecurite | `cyber`, `pentester`, `soc\s+anal` |
| Chef de Projet IT | `chef\s+de\s+proj`, `scrum\s*master` |
| Admin Systemes & Reseaux | `sysadmin`, `réseau\s+inf` |
| Architecte IT | `architect(e)?\s+(log\|tech\|data\|cloud)` |

**Cas limites :**

| Cas limite | Traitement |
|------------|------------|
| Titre non reconnu par aucun pattern | → `profil_normalise = 'Autre IT'` |
| Titre correspondant à plusieurs patterns | → Premier match gagnant (ordre de définition) |
| Titre `null` / `NaN` | → `str.contains(na=False)` → classé `'Autre IT'` |
| Titres en majuscules (`INGÉNIEUR DATA`) | → `.str.lower()` avant matching |

**Résultat mesuré :** ~0-5% classés `'Autre IT'` (données synthétiques bien couvertes).

---

### T2.3 — Normalisation des Salaires (`normaliser_salaires`)

| Paramètre | Valeur |
|-----------|--------|
| **Lignes avant** | 5 000 offres |
| **Lignes après** | 5 000 offres |
| **Colonnes créées** | `salaire_min_mad`, `salaire_max_mad`, `salaire_median_mad`, `salaire_connu` |

**Règle appliquée :** Parsing multi-format → normalisation en MAD mensuel brut.

**Transformations successives :**
1. Valeurs non-salaires → `None` (null, confidentiel, "selon profil", vide, "à négocier")
2. Détection EUR → conversion × 10.8 (taux fixe EUR→MAD)
3. Notation `K` → × 1 000 (ex: `15K` → `15000`)
4. Extraction des montants via regex `\d+(?:\.\d+)?`
5. Fourchette (≥2 nombres) → `min` et `max`
6. Valeur unique → `min = max`
7. Validation de cohérence : `3 000 ≤ salaire ≤ 100 000 MAD`
8. `salaire_median = (min + max) / 2`

**Formats de salaires rencontrés :**
| Format source | Exemple | Résultat |
|--------------|---------|----------|
| Fourchette MAD | `15000-20000 MAD` | min=15000, max=20000 |
| Fourchette K | `15K-20K` | min=15000, max=20000 |
| Fourchette EUR | `1500-2000 EUR` | min=16200, max=21600 |
| Valeur EUR avec € | `1800€-2500€` | min=19440, max=27000 |
| Valeur unique | `12000 MAD` | min=max=12000 |
| Non renseigné | `Selon profil`, `null`, `""` | `salaire_connu = False` |
| Confidentiel | `Confidentiel` | `salaire_connu = False` |

**Cas limites :**

| Cas limite | Traitement |
|------------|------------|
| Salaire < 3 000 MAD (stage mal encodé) | → rejeté, `salaire_connu = False` |
| Salaire > 100 000 MAD (erreur de saisie) | → rejeté, `salaire_connu = False` |
| EUR sans taux de change dynamique | → taux fixe 10.8 (approximation) |
| `NaN` pandas | → `pd.isna()` → `salaire_connu = False` |

**Résultat mesuré :** ~60–70% des offres ont un `salaire_connu = True`.

---

### T2.4 — Normalisation de l'Expérience (`normaliser_experience`)

| Paramètre | Valeur |
|-----------|--------|
| **Lignes avant** | 5 000 offres |
| **Lignes après** | 5 000 offres |
| **Colonnes créées** | `experience_min_ans`, `experience_max_ans` |

**Règle appliquée :** Parsing textuel → valeurs numériques en années.

| Format source | Exemple | min | max |
|--------------|---------|-----|-----|
| Mots-clés débutant | `Junior`, `Débutant`, `Stage` | 0 | 2 |
| Mots-clés senior | `Senior`, `Confirmé`, `Expert` | 5 | `None` |
| Fourchette | `3 à 5 ans`, `3-5 ans` | 3 | 5 |
| Minimum seul | `min 3 ans`, `1 an minimum` | 3 | `None` |
| Nombre seul | `5` | 5 | `None` |
| `None` / absent | — | `None` | `None` |

**Cas limites :**

| Cas limite | Traitement |
|------------|------------|
| `NaN` pandas | → `pd.isna()` → `(None, None)` |
| Texte libre non parsable (`"selon profil"`) | → `(None, None)` |
| `"8+ ans"` | → regex `\d+` → `min=8`, `max=None` |

---

### T2.5 — Normalisation Villes & Contrats (`normaliser_villes_contrats`)

| Paramètre | Valeur |
|-----------|--------|
| **Lignes avant** | 5 000 offres |
| **Lignes après** | 5 000 offres |
| **Colonnes créées** | `ville_std`, `region_admin`, `type_contrat_std` |

**Règle appliquée — Villes :** Dictionnaire de mapping 30+ variantes → 10 villes standard.

| Variantes sources | Ville standardisée | Région administrative |
|------------------|-------------------|----------------------|
| `casablanca`, `CASABLANCA`, `casa`, `Casablanca ` | `Casablanca` | Casablanca-Settat |
| `rabat`, `Rabat-Salé`, `rabat sale` | `Rabat` | Rabat-Sale-Kenitra |
| `tanger`, `TANGER`, `Tangier`, `Tanger-Tétouan` | `Tanger` | Tanger-Tetouan-Al Hoceima |
| `marrakech`, `MARRAKECH`, `Marrakesh` | `Marrakech` | Marrakech-Safi |
| `Fès`, `fes`, `FES`, `Fez` | `Fes` | Fes-Meknes |
| `agadir`, `AGADIR` | `Agadir` | Souss-Massa |
| `Kénitra`, `kenitra` | `Kenitra` | Rabat-Sale-Kenitra |
| `Tétouan`, `tetouan` | `Tetouan` | Tanger-Tetouan-Al Hoceima |

**Cas limites — Villes :**

| Cas limite | Traitement |
|------------|------------|
| Ville vide / `NaN` / `None` | → `"Inconnue"` |
| Ville non reconnue dans le mapping | → `.strip().title()` (conservation avec mise en forme) |
| Espace trailing (`"Casablanca "`) | → clé avec espace dans le mapping |

**Règle appliquée — Contrats :** Mapping 15+ variantes → 4 types standard.

| Variantes sources | Type standardisé |
|------------------|-----------------|
| `CDI`, `cdi`, `Permanent`, `Contrat à durée indéterminée` | `CDI` |
| `CDD`, `cdd`, `Contrat à durée déterminée` | `CDD` |
| `Freelance`, `freelance`, `Mission`, `Indépendant` | `Freelance` |
| `Stage`, `stage`, `Stage PFE`, `Internship` | `Stage` |

**Cas limites — Contrats :**

| Cas limite | Traitement |
|------------|------------|
| Contrat vide / `NaN` | → `"Non precise"` |
| Valeur non reconnue | → conservation brute `.strip()` |

---

### T2.6 — Normalisation des Dates (`normaliser_dates`)

| Paramètre | Valeur |
|-----------|--------|
| **Lignes avant** | 5 000 offres |
| **Lignes après** | 5 000 offres |
| **Colonnes créées** | `date_publication` (normalisée), `date_expiration` (normalisée), `annee`, `mois`, `date_coherente` |

**Règle appliquée :** Conversion vers format ISO `YYYY-MM-DD`, extraction `annee`/`mois`, flag de cohérence.

| Format source | Fréquence | Traitement |
|--------------|-----------|------------|
| `YYYY-MM-DD` | ~90% | Validation regex → conservation |
| `DD/MM/YYYY` | ~10% | Regex capture → réorganisation |
| Valeur invalide / vide | <1% | → `None` |

**Validation de cohérence :**
- Règle : `date_publication ≤ date_expiration`
- Cas générés intentionnellement dans les données synthétiques : **5% d'incohérences** (~250 offres)
- Traitement : flag `date_coherente = False` (offres **conservées**, pas supprimées)

---

### T2.7 — Déduplication (`drop_duplicates`)

| Paramètre | Valeur |
|-----------|--------|
| **Lignes avant** | 5 000 offres |
| **Doublons supprimés** | 0 (données synthétiques avec ID unique) |
| **Lignes après** | 5 000 offres |

**Règle appliquée :** `df.drop_duplicates(subset='id_offre', keep='first')`  
**Format des IDs :** `{PREFIX}-{YYYY}-{NNNNN}` ex. `RK-2023-00042` → unicité garantie par le générateur.

---

## ÉTAPE 3 — Silver NLP (`silver_nlp.py`)

### Objectif
Extraire les compétences IT depuis le texte libre et les champs `competences_brut` + `description` de chaque offre.

| Paramètre | Valeur |
|-----------|--------|
| **Lignes avant (offres)** | 5 000 offres Silver |
| **Lignes après (compétences)** | ~26 711 lignes (une ligne par compétence par offre) |
| **Fichier produit** | `silver/competences_extraites/competences.parquet` |

---

### T3.1 — Construction du Dictionnaire de Compétences

**Règle appliquée :** Lecture du référentiel JSON → dictionnaire plat `{alias: {competence, famille}}`.

| Famille | Exemples de compétences | Nb aliases |
|---------|------------------------|------------|
| `langages` | Python, JavaScript, Java, SQL, R, TypeScript, Scala, Bash | ~40 |
| `frameworks_web` | React, Angular, Vue, Django, Spring, Flutter | ~20 |
| `data_engineering` | Spark, Kafka, Airflow, dbt, Hadoop, Pandas | ~15 |
| `cloud` | AWS, GCP, Azure | ~15 |
| `bi_analytics` | Power BI, Tableau, Metabase, Excel, Jupyter | ~10 |
| `devops_infra` | Docker, Kubernetes, Jenkins, Terraform, Git, Linux | ~20 |
| `databases` | PostgreSQL, MySQL, MongoDB, Redis, Firebase | ~15 |
| `data_science_ml` | Machine Learning, TensorFlow, PyTorch, NLP | ~15 |
| `methodologies` | Agile, Scrum, JIRA, UML | ~8 |
| `securite` | Firewall, SIEM, Pentest, ISO 27001 | ~8 |
| `autres` | REST API, Microservices, Figma, Networking | ~8 |

**Total : 80+ compétences normalisées, ~175+ aliases**

---

### T3.2 — Extraction par Word-Boundary Matching

**Règle appliquée :**
1. Concaténation `competences_brut + " " + description` → texte unifié en minuscules
2. Tri des aliases par longueur décroissante (éviter faux positifs ex: `"r"` avant `"react"`)
3. Pour chaque alias : `re.search(r'\b' + re.escape(alias) + r'\b', texte)`
4. Une compétence normalisée par offre (pas de doublon `python` si détecté 2 fois)
5. Offre sans compétence → 1 ligne `competence='non_detecte'`, `famille='inconnu'`

**Cas limites :**

| Cas limite | Traitement |
|------------|------------|
| Alias court ambigu (`"r"`, `"go"`) | → word-boundary `\b` limite les faux positifs |
| `"R"` dans un titre (`"Développeur R"`) | → `.lower()` + `\b` → détecté |
| Séparateurs variés dans `competences_brut` (`, `, ` / `, ` • `, `\n`) | → matching sur texte brut unifié, séparateurs ignorés |
| Compétence détectée via description ET competences_brut | → dédupliquée par `set()` |
| Offre avec `None` dans les champs texte | → `str(... or '')` → chaîne vide |
| Résultat : `"non_detecte"` | → offres conservées pour traçabilité |

**Taux de couverture mesuré :** ~95–98% des offres ont au moins 1 compétence détectée (données synthétiques bien couvertes par le référentiel).

---

## ÉTAPE 4 — Gold Aggregation (`gold_aggregation.py`)

### Objectif
Construire 5 tables analytiques via DuckDB SQL directement sur les fichiers Parquet Silver.

**Moteur :** DuckDB (in-memory, sans serveur)  
**Sources :** `silver/offres_clean/offres_clean.parquet` + `silver/competences_extraites/competences.parquet`

---

### T4.1 — Table `top_competences.parquet`

| Paramètre | Valeur |
|-----------|--------|
| **Source** | `competences.parquet` |
| **Lignes produites** | 196 lignes |

**Règle appliquée :**
- Exclure `competence = 'non_detecte'`
- `COUNT(DISTINCT id_offre)` par `(profil, famille, competence)`
- `RANK() OVER (PARTITION BY profil ORDER BY nb_offres DESC)` → rang dans chaque profil
- Union avec agrégat global (`profil = 'tous'`)
- `pct_offres_total` = % sur total des offres avec compétence

**Cas limites :**
- Compétence apparaissant dans un seul profil → rang = 1 dans ce profil
- `profil = NULL` (offre sans profil normalisé) → incluse dans groupe `NULL` de DuckDB

---

### T4.2 — Table `salaires_par_profil.parquet`

| Paramètre | Valeur |
|-----------|--------|
| **Source** | `offres_clean.parquet` |
| **Lignes produites** | 371 lignes |

**Règle appliquée :**
- Groupement par `(profil_normalise, ville_std, type_contrat_std)`
- Filtrage `HAVING COUNT(*) >= 3` (minimum statistique)
- `MEDIAN`, `AVG`, `PERCENTILE_CONT(0.25)`, `PERCENTILE_CONT(0.75)` sur `salaire_median_mad` filtré `WHERE salaire_connu = true`
- `MIN(salaire_min_mad)`, `MAX(salaire_max_mad)` = bornes observées

**Cas limites :**
- Groupe avec 0 salaires connus → `salaire_median_mad = NULL` (conservation du groupe, métriques nulles)
- Groupe avec < 3 offres → exclu par `HAVING` (pas assez représentatif statistiquement)

---

### T4.3 — Table `offres_par_ville.parquet`

| Paramètre | Valeur |
|-----------|--------|
| **Source** | `offres_clean.parquet` |
| **Lignes produites** | 1 930 lignes |

**Règle appliquée :**
- Groupement par `(ville_std, region_admin, profil_normalise, annee, mois)`
- `COUNT(*) FILTER (WHERE teletravail ILIKE '%hybride%' OR ... '%remote%' OR ... '%teletravail%')` → nb offres remote
- `pct_remote` = ratio remote / total (avec `NULLIF(COUNT(*), 0)`)

**Cas limites :**
- Ville `'Inconnue'` → incluse comme groupe distinct
- `teletravail = NULL` → non compté dans le filtre remote (comportement SQL standard)
- `pct_remote = NULL` si `nb_offres = 0` → protégé par `NULLIF`

---

### T4.4 — Table `entreprises_recruteurs.parquet`

| Paramètre | Valeur |
|-----------|--------|
| **Source** | `offres_clean.parquet` |
| **Lignes produites** | 100 lignes (TOP 100) |

**Règle appliquée :**
- Filtre `entreprise IS NOT NULL AND entreprise != ''`
- Groupement par `(entreprise, ville_std)`
- `HAVING COUNT(*) >= 2` (minimum 2 offres publiées)
- `LIST(DISTINCT profil_normalise ORDER BY profil_normalise)` → liste des profils recrutés
- `LIMIT 100 ORDER BY nb_offres_publiees DESC`

**Cas limites :**
- Entreprise présente dans plusieurs villes → une ligne par ville (combinaison unique)
- Salaire moyen `NULL` si aucune offre avec salaire connu → comportement DuckDB standard
- `premiere_offre` / `derniere_offre` → `MIN/MAX(date_publication)` (type string YYYY-MM-DD → tri lexicographique correct)

---

### T4.5 — Table `tendances_mensuelles.parquet`

| Paramètre | Valeur |
|-----------|--------|
| **Source** | `offres_clean.parquet` |
| **Lignes produites** | 322 lignes |

**Règle appliquée :**
- Filtre `annee IS NOT NULL`
- Groupement par `(annee, mois, profil_normalise)`
- `LAG(COUNT(*)) OVER (PARTITION BY profil_normalise ORDER BY annee, mois)` → volume du mois précédent

**Cas limites :**
- Premier mois d'un profil → `nb_offres_mois_precedent = NULL` (comportement normal de `LAG`)
- Mois sans offres pour un profil → ligne absente (pas de ligne à 0 offres)
- Tri `ORDER BY annee, mois` sur chaînes (`"2023"`, `"01"`) → tri lexicographique correct car zero-padded

---

## Synthèse des Cas Limites Globaux

| Catégorie | Cas limite | Fréquence estimée | Traitement adopté | Impact |
|-----------|-----------|-------------------|-------------------|--------|
| **Dates** | Format `DD/MM/YYYY` | ~10% | Regex + réorganisation | Aucun (0 perte) |
| **Dates** | Date expiration < publication | ~5% | Flag `date_coherente=False` | Offre conservée |
| **Dates** | Date invalide/absente | <1% | → `None` | Offre conservée |
| **Salaires** | Format non parsable | ~30–40% | → `salaire_connu=False` | Métriques partielles |
| **Salaires** | Hors plage [3000-100000] MAD | <5% | → `salaire_connu=False` | Filtrage silencieux |
| **Salaires** | EUR sans taux dynamique | ~5% | Taux fixe 10.8 | Approximation |
| **Villes** | Variantes orthographiques | 100% | Dictionnaire mapping 30+ | Standardisation complète |
| **Villes** | Ville inconnue | <2% | `.title()` + conservation | Groupe `Autre` en analyse |
| **Contrats** | Variantes textuelles | 100% | Mapping 4 types | Standardisation complète |
| **NLP** | Alias court ambigu (`"r"`) | ~1% | `\b` word-boundary | Faux positifs limités |
| **NLP** | 0 compétence détectée | ~2–5% | Ligne `non_detecte` | Traçabilité conservée |
| **Titres** | Non reconnu par regex | ~0–5% | → `'Autre IT'` | Groupe résiduel |
| **Gold** | Groupe < 3 offres | Variable | `HAVING COUNT(*) >= 3` | Exclusion statistique |

---

## Qualité des Données — Métriques Finales

| Indicateur | Valeur |
|-----------|--------|
| Offres ingérées Bronze | 5 000 |
| Offres Silver après déduplication | 5 000 |
| Offres avec profil reconnu | ~95–100% |
| Offres avec salaire valide | ~60–70% |
| Offres avec date cohérente | ~95% |
| Offres avec ≥1 compétence NLP | ~95–98% |
| Tables Gold produites | 5 |
| Durée totale pipeline | ~15 secondes |

---

*Rapport généré — Mexora RH Intelligence © 2024*
