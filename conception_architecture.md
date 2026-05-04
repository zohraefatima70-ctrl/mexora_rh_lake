# Document de Conception — Architecture Data Lake Mexora RH

## 1. Justification des Formats de Stockage

L'architecture du Data Lake est structurée en trois zones (Medallion Architecture), chacune ayant un format de stockage adapté à son rôle spécifique.

| Zone             | Format choisi     | Pourquoi ce format ?                                                                                                                                                                                                                                                  | Pourquoi pas les autres ?                                                                                                                                                                                           |
| ---------------- | ----------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Bronze** | **JSON**    | Il s'agit du format natif d'extraction des sources (API, scraping). Le JSON permet de préserver la hiérarchie et la flexibilité des données semi-structurées brutes (ex: listes de compétences, textes libres) sans imposer de schéma rigide.                  | Le CSV aplatit les listes et gère mal les retours à la ligne dans les descriptions. Le Parquet imposerait un schéma strict trop tôt, risquant de rejeter des données mal formées lors de l'ingestion.         |
| **Silver** | **Parquet** | Format orienté colonne, fortement compressé (Snappy) et typé. Idéal pour des données nettoyées et tabulaires. Il permet des lectures partielles de colonnes très performantes et réduit considérablement l'espace de stockage.                               | Le CSV est trop volumineux, lent à parser et ne conserve pas les types de données natifs (tout est chaîne de caractères). Le JSON est verbeux et inefficace pour des requêtes analytiques sur de gros volumes. |
| **Gold**   | **Parquet** | Mêmes avantages que pour la zone Silver. Le format Parquet est nativement optimisé pour être interrogé par des moteurs OLAP comme DuckDB. Il permet l'exécution de requêtes d'agrégation complexes avec une très faible latence directement sur les fichiers. | Une base de données relationnelle (PostgreSQL) ajouterait une dépendance serveur lourde pour des données purement analytiques (froid/tiède). Le CSV n'est pas optimisé pour l'analytique.                      |

## 2. Questions de Conception

### Pourquoi conserver les données brutes en zone Bronze sans les modifier ? Quels risques si on ne le fait pas ?

La zone Bronze agit comme un **historique immuable (Source of Truth)**. On la conserve telle quelle pour pouvoir rejouer les pipelines de transformation en cas de bug dans la logique de nettoyage (zone Silver) ou si de nouvelles règles métier apparaissent (ex: extraire une nouvelle information depuis la description textuelle).
**Risques** : Si on modifie les données dès l'ingestion et qu'on perd le format d'origine, toute erreur de transformation est irréversible (perte de données).

### Qu’est-ce que le “schema-on-read” ? En quoi est-ce différent du DWH du miniprojet 1 (“schema-on-write”) ?

- **Schema-on-read (Data Lake)** : Les données sont stockées telles quelles (JSON brut). Le schéma et la structure ne sont appliqués qu'au moment où l'on lit les données pour les transformer (passage Bronze → Silver). Cela permet d'ingérer n'importe quoi très rapidement.
- **Schema-on-write (Data Warehouse)** : Le schéma des tables (types de colonnes, contraintes de clés) est défini à l'avance. Les données sont validées et transformées avant d'être écrites dans la base. Si la donnée ne respecte pas le schéma, elle est rejetée à l'insertion.

### Comment définit-on la partition dans chaque zone ? Justifier les choix.

Le partitionnement physique (dossiers) optimise le temps de requête et la gestion du cycle de vie des données.

- **Bronze (`par_source/par_mois`)** : L'ingestion se fait par lots depuis différents sites (Rekrute, LinkedIn). Séparer par source permet de gérer des ingestions indépendantes. Le partitionnement par mois facilite l'archivage ou la suppression des données très anciennes (Data Lifecycle Management).
- **Silver (`par_ville/par_mois` ou `offres_clean`)** : Une fois nettoyées, l'origine de la donnée (source) importe peu pour l'analyse métier. Les analystes requêtent souvent les données par géographie (ville) ou par temporalité (mois) pour observer des tendances. *Note: Dans notre implémentation locale, nous avons consolidé dans un seul fichier Parquet pour simplifier l'utilisation avec DuckDB, mais l'approche théorique recommanderait un partitionnement par mois pour l'évolutivité.*

### Comment éviter que le Data Lake devienne un “Data Swamp” ?

Un "Data Swamp" (marécage de données) est un Data Lake où les données sont désorganisées, non documentées et inexploitables. Règles de gouvernance :

1. **Catalogage des données (Data Catalog)** : Maintenir des métadonnées strictes (schémas attendus, dictionnaire de données).
2. **Zones strictes** : Séparation hermétique entre Bronze, Silver et Gold. Les utilisateurs métiers n'accèdent qu'à la zone Gold.
3. **Qualité des données** : Monitoring des taux de rejets et des anomalies lors du passage de Bronze à Silver.
4. **Gestion du cycle de vie** : Purge ou archivage à froid des données Bronze obsolètes.

## 3. Flux des Données et Utilisateurs

1. **Zone Bronze (JSON)** : Consommée uniquement par le **Data Engineer** (Pipeline d'ingestion et script de nettoyage).
2. **Zone Silver (Parquet)** : Consommée par le **Data Engineer** (pour construire la zone Gold) et le **Data Scientist** (pour entraîner des modèles ML sur des données propres mais non agrégées, ex: NLP sur les descriptions).
3. **Zone Gold (Parquet)** : Consommée par le **Data Analyst**, les outils de **BI** (Power BI) et l'équipe RH via DuckDB, pour la création de dashboards et de rapports.
