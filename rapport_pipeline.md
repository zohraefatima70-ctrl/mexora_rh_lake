# Rapport Pipeline — Mexora RH Intelligence Data Lake

## Résumé des transformations

| Étape | Entrée | Sortie | Durée |
|-------|--------|--------|-------|
| Bronze Ingestion | 5 000 offres JSON brutes | 69 fichiers partitionnés | ~1s |
| Silver Transform | 5 000 offres Bronze | 5 000 offres Parquet nettoyées | ~3s |
| Silver NLP | 5 000 offres Silver | 26 711 lignes compétences | ~8s |
| Gold Aggregation | 2 Parquet Silver | 5 tables Gold | ~2s |

---

## ÉTAPE 1 — Bronze Ingestion

### Règle appliquée
Chargement brut sans aucune modification. Partitionnement par `source` (rekrute / marocannonce / linkedin) et par `mois` de publication (YYYY_MM).

### Statistiques

| Source | Offres |
|--------|--------|
| rekrute | 2 280 |
| linkedin | 1 469 |
| marocannonce | 1 251 |
| **Total** | **5 000** |

- **Partitions créées** : 69 fichiers `offres_raw.json`
- **Lignes avant** : 5 000 | **Lignes après** : 5 000 (immuable)

### Cas limites
- Dates au format `DD/MM/YYYY` → détectées et converties pour le partitionnement uniquement (la donnée brute est conservée intacte)
- Offres sans source → classées dans partition `inconnu/date_inconnue`

---

## ÉTAPE 2 — Silver Transform (Nettoyage)

### 2.1 Normalisation des titres de poste

**Règle** : mapping regex vers 13 familles de profils IT. Priorité : premier match appliqué.

| Résultat | Valeur |
|----------|--------|
| Offres classifiées | 4 622 / 5 000 (92.4%) |
| Offres « Autre IT » | 378 (7.6%) |

**Cas limites** :
- "ETL Developer" → Data Engineer (via pattern `etl.*dev`)
- "Reporting Officer" → Data Analyst (via pattern `reporting.*officer`)
- "UI Developer" → Développeur Frontend (via pattern `ui.*dev`)
- Titres très génériques ("Informaticien", "Développeur") → conservés en « Autre IT »

### 2.2 Normalisation des salaires

**Règles** :
- Fourchettes `15000-20000 MAD` → salaire_min=15000, salaire_max=20000, median=17500
- Suffixe K → ×1000 (ex: `15K` → 15000)
- EUR → MAD au taux fixe 1€ = 10.8 MAD (taux 2024)
- `Selon profil`, `Confidentiel`, null → salaire_connu=False
- Plages invalides (<3000 ou >100000 MAD) → rejetées

| Résultat | Valeur |
|----------|--------|
| Salaires valides | 80.7% des offres |
| Salaires non renseignés | 19.3% |

**Cas limites** :
- `"1500-2000 EUR"` → 16200–21600 MAD (conversion EUR)
- `"5000 MAD"` (valeur unique) → sal_min = sal_max = 5000
- `"35000-45000 MAD"` → valide, conservé
- `"100 MAD"` → rejeté (< 3000 MAD, incohérent)

### 2.3 Normalisation de l'expérience

**Règles** :
- `"3-5 ans"` → min=3, max=5
- `"3 à 5 ans"` → min=3, max=5
- `"min 3 ans"` → min=3, max=None
- `"Débutant accepté"`, `"Junior"` → min=0, max=2
- `"Senior"`, `"Confirmé"`, `"Expert"` → min=5, max=None
- `null` → min=None, max=None

### 2.4 Normalisation des villes

**Règle** : dictionnaire de mapping vers forme standard. Ex: `"casa"`, `"CASABLANCA"`, `"Casablanca "` → `"Casablanca"`.

| Ville std | Variantes traitées |
|-----------|--------------------|
| Casablanca | casa, CASABLANCA, Casablanca (espace) |
| Rabat | rabat-sale, RABAT |
| Tanger | tangier, TANGER, Tanger-Tétouan |
| Fes | Fès, fez, FES |

### 2.5 Normalisation des contrats

`"cdi"`, `"Contrat à durée indéterminée"`, `"Permanent"` → `"CDI"`

### 2.6 Normalisation des dates

- Format `DD/MM/YYYY` → `YYYY-MM-DD`
- **Dates incohérentes détectées** : 255 (publication > expiration) → flaggées `date_coherente=False`, conservées

---

## ÉTAPE 3 — Silver NLP (Extraction Compétences)

### Règle appliquée
Matching regex par mot entier (`\b`) sur la concaténation de `competences_brut` + `description`. Tri des alias par longueur décroissante pour éviter les faux positifs (`node.js` avant `node`).

### Statistiques

| Résultat | Valeur |
|----------|--------|
| Lignes compétences produites | 26 711 |
| Offres avec ≥1 compétence | 5 000 / 5 000 (100%) |
| Compétences distinctes détectées | ~40 |
| Familles couvertes | 13 |

**Cas limites** :
- `"R"` (langage) : alias `\br\b` peut matcher faux positifs → traité par tri longueur + word boundary
- `"node"` vs `"node.js"` → `node.js` testé en premier car plus long
- Compétences avec caractères spéciaux (`c#`, `ci/cd`) → `re.escape()` appliqué

---

## ÉTAPE 4 — Gold Aggregation

### Règles DuckDB appliquées

**top_competences** : `RANK() OVER (PARTITION BY profil ORDER BY COUNT DESC)` → rang par profil  
**salaires_par_profil** : `MEDIAN()`, `PERCENTILE_CONT(0.25/0.75)`, filtre `nb_offres >= 3`  
**offres_par_ville** : agrégat par ville+profil+annee+mois, calcul % remote  
**entreprises_recruteurs** : `LIST(DISTINCT)` pour profils recrutés, top 100  
**tendances_mensuelles** : `LAG()` pour évolution mois précédent  

### Statistiques

| Table Gold | Lignes |
|-----------|--------|
| top_competences | 196 |
| salaires_par_profil | 371 |
| offres_par_ville | 1 930 |
| entreprises_recruteurs | 100 |
| tendances_mensuelles | 322 |

---

## Conclusion

Le pipeline traite 5 000 offres brutes en ~15 secondes et produit des données analytiques exploitables immédiatement via DuckDB. Le taux de classification des titres (92.4%) et de renseignement des salaires (80.7%) sont satisfaisants pour une analyse de marché.
