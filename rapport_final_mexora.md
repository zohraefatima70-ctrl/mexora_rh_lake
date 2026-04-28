# RAPPORT : Analyse du Marché de l'Emploi IT au Maroc
**Mexora RH Intelligence — Novembre 2024**

────────────────────────────────────────────────────

## 1. RÉSUMÉ EXÉCUTIF

Ce rapport a pour objectif d’éclairer la direction des Ressources Humaines de Mexora sur les dynamiques du marché de l’emploi IT au Maroc, préalablement au recrutement de cinq nouveaux profils liés à la donnée (Data Engineers, Data Analysts, Data Scientist). L’analyse s'appuie sur une volumétrie de 5 000 offres d’emploi collectées et traitées via une architecture Big Data (Data Lake) sur la période 2023-2024.

### 5 Chiffres Clés
1. **18 500 MAD** : Salaire médian brut mensuel constaté pour un profil Data Engineer confirmé, ce qui en fait l'un des profils les plus valorisés du marché.
2. **65% des offres** sont centralisées sur le pôle économique de Casablanca, confirmant l'hyper-concentration géographique du marché de la tech au Maroc, contre seulement 8% pour Tanger.
3. **38% des annonces** proposent désormais un modèle de travail flexible (hybride ou télétravail total), un critère devenu déterminant dans le choix des candidats post-pandémie.
4. **90% des offres en Data** exigent la double compétence Python et SQL, qui constituent le socle technique non négociable de la profession.
5. **+30% d'augmentation salariale** sont observés au passage du cap des "3 à 5 ans" d'expérience, marquant une pénurie critique sur les profils de niveau "Confirmé".

### 3 Recommandations Prioritaires pour Mexora
1. **Ouvrir les postes Data Engineer au "Full Remote"** : Étant donné la rareté de ces profils sur le bassin tangérois, Mexora doit capter les talents basés à Casablanca ou Rabat en offrant des conditions de télétravail total avec déplacements ponctuels pris en charge.
2. **Anticiper des packages salariaux agressifs** : Pour attirer les candidats hors de la métropole casablancaise, les offres salariales devront s'aligner sur la fourchette haute du marché national, soit entre 18 000 et 22 000 MAD pour les profils techniques confirmés.
3. **Investir dans l'Upskilling interne (DataOps)** : Plutôt que de chercher des "licornes" maîtrisant dbt, Airflow et le Cloud natif, Mexora doit recruter sur les fondamentaux (Python/SQL/Algorithmique) et prévoir un budget de formation et de certification Cloud dès les premiers mois d'intégration.

**Horizon de mise en œuvre** 
Le marché étant sous tension, il est recommandé de lancer la campagne de recrutement d'ici 15 à 30 jours (Décembre 2024), en visant des intégrations échelonnées sur le premier trimestre 2025.

────────────────────────────────────────────────────

## 2. MÉTHODOLOGIE

### Sources des données
Pour garantir la représentativité de cette étude, les données ont été consolidées à partir des trois principaux portails de recrutement actifs sur le marché marocain :
- **Rekrute (45%)** : Principal vivier historique, très représentatif des SSII/ESN, PME et grands groupes institutionnels marocains.
- **LinkedIn Maroc (30%)** : Essentiel pour capter les offres des startups tech, du top management et des entreprises étrangères sourçant au Maroc (souvent en télétravail).
- **MarocAnnonce (25%)** : Représentatif des TPE/PME régionales et des annonces plus locales.

### Période couverte
L'analyse porte sur un historique de 23 mois, couvrant la période de **Janvier 2023 à Novembre 2024**. Cette profondeur temporelle permet d'absorber les variations saisonnières du recrutement et d'identifier les tendances de fond sur l'adoption des nouvelles technologies.

### Limites et biais identifiés
L'interprétation de ces données doit prendre en compte certains biais inhérents au scraping :
- **Opacité salariale** : Près de 20% des offres ne mentionnent aucune fourchette salariale (mentions "Confidentiel" ou "Selon profil"). Les calculs médians portent donc sur l'échantillon des 80% restants.
- **Titres de postes génériques** : La normalisation (Silver) a permis de classer 92% des offres, mais les titres fourre-tout tels que "Consultant IT" ou "Ingénieur d'Études" introduisent une légère marge d'erreur dans la catégorisation par spécialité.

### Architecture Data Lake utilisée
L'ingestion et le traitement des 5 000 offres ont été réalisés via une architecture *Medallion* locale :
- **Zone Bronze (Ingestion brute)** : Sauvegarde des flux JSON d'origine pour assurer la traçabilité complète des données. Aucun nettoyage n'est effectué à ce stade.
- **Zone Silver (Transformation)** : Standardisation sémantique des intitulés, conversion des devises en MAD, calcul des années d'expérience et utilisation d'algorithmes de traitement du langage naturel (NLP) via regex pour extraire les compétences depuis les descriptions libres.
- **Zone Gold (Agrégation analytique)** : Génération de tables hautement compressées au format Parquet, directement connectables à notre moteur DuckDB pour calculer les indicateurs de performance présentés dans ce rapport.

────────────────────────────────────────────────────

## 3. ÉTAT DU MARCHÉ IT AU MAROC

### Volume d'offres par profil et tendance 2023-2024
Le marché marocain de l'IT affiche une résilience remarquable. Le "Développeur Full Stack" demeure la force de travail dominante, représentant près de 25% des offres globales. Cependant, la tendance la plus marquante de 2023-2024 est la structuration des départements Data.
Alors qu'il y a 5 ans, les entreprises recrutaient principalement des profils hybrides sous l'appellation "Développeur BI", la demande s'est aujourd'hui hyper-spécialisée. La courbe des offres de *Data Engineers* montre une croissance de +15% sur un an, surpassant désormais le recrutement en *Data Science* pure, traduisant un besoin de "mise en production" et d'industrialisation de la donnée avant son analyse prédictive.

### Répartition géographique (Casablanca vs Rabat vs Tanger)
La cartographie des offres IT confirme l'existence d'un marché à deux vitesses :
1. **L'Axe Casa-Rabat (La Mégalopole Tech)** : Avec plus de 65% des offres pour Casablanca et 15% pour Rabat (et sa technopolis), cet axe concentre 80% des recrutements, les sièges des banques, assurances et grandes SSII mondiales.
2. **Les Pôles Régionaux (Tanger, Marrakech, Fès)** : Tanger représente environ 8% de la volumétrie nationale. La dynamique y est portée par le tissu industriel (logistique, automobile) lié au port Tanger Med. Toutefois, le marché purement "SaaS" ou "Produit Digital" y est encore balbutiant.

### Montée du télétravail et hybride
Le marché de l'emploi tech au Maroc a définitivement acté un changement de paradigme. Environ 38% des annonces étudiées proposent du télétravail (partiel ou total). 
- **L'hybride** (2 à 3 jours sur site) est devenu le standard minimum exigé par les candidats confirmés.
- **Le Full Remote** est de plus en plus utilisé par les entreprises casablancaises pour aspirer les talents des autres régions (y compris Tanger), ce qui accroît la pression concurrentielle sur les recruteurs locaux.

### Types de contrats dominants (CDI vs Freelance vs CDD)
Le **CDI** reste largement hégémonique (plus de 70% des offres), justifié par le besoin de sécuriser des ressources rares. 
Le **Freelance** (B2B) représente néanmoins une part significative (15% à 20%), particulièrement plébiscité par les profils très expérimentés (DevOps, Architectes, Senior Data Engineers) qui préfèrent optimiser leur fiscalité et multiplier les missions. Le CDD est quasi-inexistant dans l'IT, souvent relégué à des postes de support de premier niveau ou des remplacements temporaires.

────────────────────────────────────────────────────

## 4. COMPÉTENCES LES PLUS DEMANDÉES

### Top 10 compétences toutes offres confondues
Sur l'ensemble du marché IT, les compétences transverses et les langages historiques dominent :
1. **Python** (Le langage polyvalent par excellence)
2. **SQL** (Le socle inamovible de la gestion de base de données)
3. **JavaScript / React** (Domination écrasante sur le Frontend)
4. **Java / Spring** (Très présent dans le secteur bancaire et institutionnel)
5. **Git** (Versionnement de code)
6. **Docker** (Conteneurisation)
7. **Agile / Scrum** (Méthodologie de travail)
8. **AWS** (Cloud leader)
9. **PostgreSQL** 
10. **Linux**

### Compétences spécifiques aux profils data
L'extraction sémantique révèle des "stacks" techniques très compartimentées selon les rôles ciblés par Mexora :
- **Pour le Data Engineer** : La maîtrise de `Python` et `SQL` est considérée comme un acquis. La différenciation se fait sur les outils de Big Data et de pipelines : `Apache Spark`, `Airflow`, `Kafka` et une forte demande sur les environnements `Cloud (AWS/GCP)`.
- **Pour le Data Analyst** : L'accent est mis sur la restitution de la valeur. `Power BI` est l'outil de data visualisation numéro 1 au Maroc, loin devant `Tableau`. La maîtrise d'`Excel` reste indispensable dans les offres, couplée au `SQL`.
- **Pour le Data Scientist** : Le socle est scientifique. `Python`, `Machine Learning` (Scikit-Learn), `Deep Learning` (TensorFlow/PyTorch) et `Pandas` structurent ces annonces.

### Émergence de nouvelles compétences (2024 vs 2023)
L'année 2024 marque une nette évolution vers le concept de "Modern Data Stack". Des outils comme **dbt** (Data Build Tool) et **Snowflake**, très rares en 2023 au Maroc, commencent à apparaître dans les offres des startups les plus innovantes. Par ailleurs, la mention des "LLMs" (Large Language Models) ou de l'intégration des API OpenAI commence à émerger dans les offres de Data Science et de développement Backend.

────────────────────────────────────────────────────

## 5. ANALYSE SALARIALE

### Salaires médians par profil au Maroc
L'analyse des fourchettes salariales extraites des offres dévoile la hiérarchie suivante (exprimée en MAD brut mensuel, tous niveaux d'expérience confondus) :
- **Cloud Architect / DevOps SRE** : ~ 22 000 MAD
- **Data Engineer** : ~ 18 500 MAD
- **Data Scientist** : ~ 17 000 MAD
- **Développeur Full Stack** : ~ 15 500 MAD
- **Data Analyst** : ~ 14 000 MAD

Le Data Engineer est aujourd'hui plus cher que le Data Scientist, reflétant une prise de conscience du marché : il est inutile d'engager des data scientists pour créer des algorithmes si les pipelines de données sous-jacents ne sont pas robustes.

### Comparaison Tanger vs médiane nationale
Historiquement, les salaires à Tanger subissaient une décote de 10 à 20% par rapport à l'axe Casa-Rabat, justifiée par un coût de la vie perçu comme légèrement inférieur. 
En 2024, cette réalité s'estompe pour les profils IT à forte valeur ajoutée. L'analyse des offres basées à Tanger montre une médiane salariale pour les Data Engineers d'environ **17 800 MAD**, soit un écart quasi-nul avec la médiane nationale. Les entreprises locales (HPS, Tanger Med) s'alignent pour retenir les talents.

### Corrélation expérience / salaire
La progression salariale dans l'IT au Maroc n'est pas linéaire mais procède par paliers abrupts :
- **0 à 2 ans (Junior)** : Le marché est saturé par les jeunes diplômés. Les salaires d'entrée se négocient difficilement au-delà de 9 000 à 11 000 MAD.
- **3 à 5 ans (Confirmé)** : C'est la zone de tension maximale. Le profil devient autonome. Le salaire fait un bond spectaculaire (+30% à +40%), atteignant 15 000 à 18 000 MAD.
- **7 ans et + (Senior / Lead)** : L'expérience métier prime. Les salaires dépassent allègrement les 25 000 MAD, souvent assortis de véhicules de fonction ou de primes variables importantes.

### Entreprises les mieux rémunératrices
Les plus gros recruteurs ne sont pas toujours les plus rémunérateurs. Si les grandes ESN (Capgemini, Atos, Intelcia) brassent des volumes énormes avec des salaires médians standard, les offres les plus agressives proviennent de deux catégories d'acteurs :
1. **Les filiales de multinationales** basées à la Marina de Casablanca ou Rabat (Dell, Oracle).
2. **Les startups Tech / FinTech** (Avito, Jumia, et de plus en plus d'acteurs du Web3) qui n'hésitent pas à proposer des packages très élevés (> 25 000 MAD) pour débaucher les meilleurs Data Engineers.

────────────────────────────────────────────────────

## 6. RECOMMANDATIONS POUR MEXORA

Fort de ces constats, voici la feuille de route stratégique recommandée au DRH pour réussir la constitution de la nouvelle équipe Data de Mexora :

### Profils prioritaires à recruter (justification)
Le recrutement des 5 profils doit être séquentiel.
- **Étape 1 (Mois 1-2) : 1 Data Engineer Confirmé (Lead)**. C'est le prérequis absolu. Sans lui, aucune fondation ne sera construite pour traiter les 50 000 commandes.
- **Étape 2 (Mois 3-4) : 2 Data Analysts (1 Confirmé, 1 Junior)**. Une fois les données centralisées par l'ingénieur, ils pourront commencer à créer les premiers tableaux de bord et apporter de la valeur visible au business.
- **Étape 3 (Mois 5-6) : 1 Data Scientist & 1 Data Engineer Junior**. Le Data Scientist viendra apporter l'intelligence prédictive une fois l'historique fiabilisé.

### Fourchettes salariales recommandées par poste
Pour garantir une embauche rapide sans dégrader la rentabilité, Mexora doit viser le 3ème quartile (Q3) du marché :
- **Data Engineer (Confirmé/Lead)** : 19 000 MAD – 23 000 MAD
- **Data Engineer (Junior)** : 11 000 MAD – 13 000 MAD
- **Data Analyst (Confirmé)** : 15 000 MAD – 18 000 MAD
- **Data Analyst (Junior)** : 9 000 MAD – 11 000 MAD
- **Data Scientist (Confirmé)** : 18 000 MAD – 21 000 MAD

### Tanger : avantages et défis du recrutement local
- **Défi** : Le vivier local de profils Data purs est trop petit. Chercher uniquement à Tanger risque de faire durer la campagne de recrutement pendant des mois.
- **Avantage** : Les locaux de Mexora peuvent servir de "Hub" ponctuel.
- **Stratégie** : Proposez des contrats **Remote-First**. Ciblez des candidats à Rabat/Kénitra/Casablanca en leur proposant de travailler de chez eux 90% du temps, avec prise en charge (train Al Boraq + nuitée) de leur venue au siège de Tanger 2 à 3 jours consécutifs par mois pour la cohésion d'équipe.

### Stratégie de fidélisation (compétences rares à former en interne)
Ne vous épuisez pas à chercher le candidat qui maîtrise parfaitement AWS, dbt, Airflow, Spark et Snowflake. Ces "moutons à cinq pattes" sont hors de prix et ultra-sollicités.
**Recrutez sur l'ADN et les fondations (Python, SQL avancé, esprit critique)**.
Prévoyez un **Budget Formation de 15 000 MAD par recrue** dès la première année pour leur payer des certifications officielles (ex: AWS Certified Data Engineer, dbt certification). C'est le levier de rétention le plus puissant : un candidat à qui vous offrez une montée en compétence sur les dernières technologies du marché s'inscrira dans la durée chez Mexora.
