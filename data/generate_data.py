"""
Générateur de données synthétiques pour le Data Lake Mexora RH.
Génère 5000 offres d'emploi IT marocaines avec des problèmes réalistes.
"""
import json
import random
import os
from datetime import datetime, timedelta

random.seed(42)

# ── Référentiels ──────────────────────────────────────────────────────────
SOURCES = ["rekrute", "marocannonce", "linkedin"]
SOURCES_WEIGHTS = [0.45, 0.25, 0.30]

VILLES_VARIANTS = {
    "Casablanca": ["Casablanca", "casablanca", "CASABLANCA", "casa", "Casa", "Casablanca "],
    "Rabat": ["Rabat", "rabat", "RABAT", "Rabat-Salé", "rabat sale"],
    "Tanger": ["Tanger", "tanger", "TANGER", "Tanger-Tétouan", "Tangier"],
    "Marrakech": ["Marrakech", "marrakech", "MARRAKECH", "Marrakesh"],
    "Fès": ["Fès", "Fes", "fes", "FES", "Fez"],
    "Agadir": ["Agadir", "agadir", "AGADIR"],
    "Oujda": ["Oujda", "oujda"],
    "Meknès": ["Meknès", "Meknes", "meknes"],
    "Kénitra": ["Kénitra", "Kenitra", "kenitra"],
    "Tétouan": ["Tétouan", "Tetouan", "tetouan"],
}
VILLES_WEIGHTS = [0.35, 0.20, 0.12, 0.08, 0.06, 0.05, 0.04, 0.04, 0.03, 0.03]

TITRES_POSTES = {
    "Data Engineer": [
        "Data Engineer", "Data Eng.", "Ingénieur Data", "Dev Data Eng",
        "Ingénieur Big Data", "Data Engineer Junior", "Senior Data Engineer",
        "ETL Developer", "Pipeline Developer", "Ingénieur ETL",
    ],
    "Data Analyst": [
        "Data Analyst", "Analyste Data", "BI Analyst", "Business Intelligence Analyst",
        "Développeur BI", "Reporting Analyst", "Data Analyste Junior",
        "Ingénieur BI", "Reporting Officer", "Analyste Données",
    ],
    "Data Scientist": [
        "Data Scientist", "Machine Learning Engineer", "ML Engineer",
        "IA Engineer", "Deep Learning Engineer", "NLP Engineer",
        "Data Scientist Junior", "Senior Data Scientist",
    ],
    "Développeur Full Stack": [
        "Développeur Full Stack", "Full Stack Developer", "Fullstack Dev",
        "Développeur Full Stack React/Node.js", "Full Stack Engineer",
        "Développeur Fullstack Java/Angular",
    ],
    "Développeur Backend": [
        "Développeur Backend", "Backend Developer", "Back-end Developer",
        "Développeur Back End Java", "Backend Engineer Python",
    ],
    "Développeur Frontend": [
        "Développeur Frontend", "Frontend Developer", "Front-end Developer",
        "Développeur Front End React", "UI Developer",
    ],
    "Développeur Mobile": [
        "Développeur Mobile", "Mobile Developer", "iOS Developer",
        "Android Developer", "Développeur Mobile Flutter",
    ],
    "DevOps / SRE": [
        "DevOps Engineer", "Ingénieur DevOps", "SRE Engineer",
        "Site Reliability Engineer", "DevOps",
    ],
    "Cloud Engineer": [
        "Cloud Engineer", "Cloud Architect", "AWS Engineer",
        "Azure Engineer", "GCP Engineer", "Cloud Admin",
    ],
    "Cybersécurité": [
        "Ingénieur Cybersécurité", "Security Engineer", "Pentester",
        "SOC Analyst", "Cybersecurity Analyst",
    ],
    "Chef de Projet IT": [
        "Chef de Projet IT", "Project Manager", "Scrum Master",
        "Chef de Projet Digital", "IT Project Manager",
    ],
    "Admin Systèmes & Réseaux": [
        "Administrateur Systèmes", "Sysadmin", "Network Engineer",
        "Ingénieur Réseau", "Admin Systèmes et Réseaux",
    ],
    "Architecte IT": [
        "Architecte Logiciel", "Architecte Technique", "Solutions Architect",
        "Architecte Data", "Architecte Cloud",
    ],
}
PROFILS_WEIGHTS = [0.08, 0.09, 0.06, 0.15, 0.10, 0.08, 0.07, 0.08, 0.05, 0.05, 0.07, 0.06, 0.06]

COMPETENCES_PAR_PROFIL = {
    "Data Engineer": ["Python", "SQL", "Spark", "Airflow", "Kafka", "AWS", "Docker", "PostgreSQL", "dbt", "Hadoop", "ETL", "Git", "Linux", "Scala", "Azure"],
    "Data Analyst": ["SQL", "Python", "Power BI", "Excel", "Tableau", "R", "Pandas", "Git", "PostgreSQL", "Metabase", "Looker", "Jupyter"],
    "Data Scientist": ["Python", "Machine Learning", "TensorFlow", "PyTorch", "SQL", "Scikit-learn", "NLP", "Deep Learning", "R", "Pandas", "Jupyter", "Git", "Docker", "AWS"],
    "Développeur Full Stack": ["JavaScript", "React", "Node.js", "HTML", "CSS", "PostgreSQL", "MongoDB", "Docker", "Git", "TypeScript", "Angular", "REST API"],
    "Développeur Backend": ["Java", "Spring Boot", "Python", "Django", "Node.js", "PostgreSQL", "MySQL", "Docker", "Git", "REST API", "Microservices", "Kafka"],
    "Développeur Frontend": ["JavaScript", "React", "Angular", "Vue.js", "HTML", "CSS", "TypeScript", "Git", "Figma", "REST API"],
    "Développeur Mobile": ["Flutter", "React Native", "Swift", "Kotlin", "Java", "Firebase", "Git", "REST API"],
    "DevOps / SRE": ["Docker", "Kubernetes", "AWS", "CI/CD", "Jenkins", "Terraform", "Linux", "Git", "Ansible", "Python", "Azure", "GCP"],
    "Cloud Engineer": ["AWS", "Azure", "GCP", "Docker", "Kubernetes", "Terraform", "Python", "Linux", "CI/CD", "Networking"],
    "Cybersécurité": ["Firewall", "SIEM", "Pentest", "Linux", "Python", "Networking", "ISO 27001", "Wireshark"],
    "Chef de Projet IT": ["Agile", "Scrum", "JIRA", "MS Project", "Git", "Communication", "Leadership"],
    "Admin Systèmes & Réseaux": ["Linux", "Windows Server", "VMware", "Cisco", "Networking", "Active Directory", "Bash"],
    "Architecte IT": ["Microservices", "AWS", "Azure", "Docker", "Kubernetes", "Java", "Python", "UML", "Design Patterns"],
}

CONTRAT_VARIANTS = {
    "CDI": ["CDI", "cdi", "Contrat à durée indéterminée", "Permanent", "CDI "],
    "CDD": ["CDD", "cdd", "Contrat à durée déterminée"],
    "Freelance": ["Freelance", "freelance", "Mission", "Indépendant"],
    "Stage": ["Stage", "stage", "Stage PFE", "Internship"],
}
CONTRAT_WEIGHTS = [0.55, 0.15, 0.15, 0.15]

EXPERIENCE_VARIANTS = [
    "3-5 ans", "3 à 5 ans", "min 3 ans", "Débutant accepté", None,
    "1-2 ans", "2-3 ans", "5-7 ans", "0-1 ans", "min 5 ans",
    "Senior (7+ ans)", "Junior", "2 à 4 ans", "sans expérience",
    "1 an minimum", "3 ans", "5 ans", "8+ ans", "Confirmé",
]

SALAIRE_VARIANTS = [
    "15000-20000 MAD", "10000-15000 MAD", "8000-12000 MAD", "20000-30000 MAD",
    "15K-20K", "10K-15K", "25K-35K", "8K-12K", "30K-40K",
    "Selon profil", None, "Confidentiel", "", "À négocier",
    "1500-2000 EUR", "2000-3000 EUR", "1800€-2500€",
    "7000 MAD", "12000 MAD", "18000 MAD", "25000 MAD",
    "6000-8000 MAD", "35000-45000 MAD", "5000-7000 MAD",
    "20K-25K MAD", "12K-18K",
]

NIVEAUX_ETUDES = ["Bac+5", "Bac+3", "Bac+2", "Bac+4", "Bac+5 et plus", None, "Ingénieur", "Master"]
SECTEURS = ["Informatique / Télécom", "Finance / Banque", "E-commerce", "Conseil", "Industrie", "Services", "Éducation"]
TELETRAVAIL = ["Présentiel", "Hybride", "Télétravail", "Remote", "Sur site", None, "Hybride (2j/semaine)"]
LANGUES = [["Français", "Anglais"], ["Français"], ["Anglais", "Français"], ["Arabe", "Français", "Anglais"], ["Français", "Anglais", "Espagnol"], None]

ENTREPRISES = [
    "TechMaroc SARL", "DataWave Maroc", "CloudFirst MA", "Digital Solutions Casablanca",
    "Capgemini Maroc", "Atos Maroc", "CGI Maroc", "Sopra Steria Maroc",
    "OCP Group", "Maroc Telecom", "Inwi", "Orange Maroc",
    "Bank of Africa", "Attijariwafa Bank", "BMCE Bank", "CIH Bank",
    "Jumia Maroc", "Avito", "HPS", "S2M",
    "Sqli Maroc", "Logware", "Omnidata", "NTT Data Maroc",
    "Deloitte Maroc", "KPMG Maroc", "EY Maroc", "PwC Maroc",
    "Majorel Maroc", "Webhelp Maroc", "Intelcia", "Altran Maroc",
    "ThalesGroup Maroc", "Bull Maroc", "Umanis Maroc", "Sofrecom Maroc",
    "IB Maroc", "M2M Group", "Involys", "Disway",
    "Tanger Med", "Renault Maroc", "PSA Maroc", "Yazaki Maroc",
    "LaFactory", "WeCode Maroc", "StartupFactory MA", "MoroccoAI",
    "Nexus IT", "AlphaData Maroc",
]

DESCRIPTIONS_TEMPLATES = [
    "Nous recherchons un {titre} expérimenté maîtrisant {comp1}, {comp2}, {comp3}. Connaissance de {comp4} et {comp5} appréciée. Le candidat devra travailler en méthode Agile avec une équipe de {n} personnes. Environnement stimulant et projets innovants.",
    "Rejoignez notre équipe en tant que {titre}. Vous serez responsable de {comp1} et {comp2}. Maîtrise de {comp3} requise. Expérience avec {comp4} est un plus. Nous offrons un environnement de travail moderne.",
    "Poste de {titre} au sein de notre département IT. Stack technique : {comp1}, {comp2}, {comp3}, {comp4}. Le candidat idéal a une solide expérience en {comp5} et travaille en autonomie.",
    "{titre} - Missions : développement et maintenance de solutions basées sur {comp1} et {comp2}. Participation aux code reviews. Utilisation de {comp3} pour le déploiement. Connaissance de {comp4} souhaitée.",
    "Offre de {titre} pour renforcer notre équipe. Technologies utilisées : {comp1}, {comp2}, {comp3}. Le poste implique {comp4} et {comp5}. Capacité à travailler en équipe et bonne communication.",
]


def generate_offre(idx, date_pub):
    """Génère une offre d'emploi avec des problèmes réalistes."""
    source = random.choices(SOURCES, weights=SOURCES_WEIGHTS, k=1)[0]
    
    # ID selon la source
    prefixes = {"rekrute": "RK", "marocannonce": "MA", "linkedin": "LI"}
    id_offre = f"{prefixes[source]}-{date_pub.year}-{idx:05d}"
    
    # Profil et titre
    profils_list = list(TITRES_POSTES.keys())
    profil = random.choices(profils_list, weights=PROFILS_WEIGHTS, k=1)[0]
    titre = random.choice(TITRES_POSTES[profil])
    
    # Ville avec variantes
    ville_key = random.choices(list(VILLES_VARIANTS.keys()), weights=VILLES_WEIGHTS, k=1)[0]
    ville = random.choice(VILLES_VARIANTS[ville_key])
    
    # Compétences
    comps = COMPETENCES_PAR_PROFIL[profil]
    nb_comp = random.randint(3, min(7, len(comps)))
    selected_comps = random.sample(comps, nb_comp)
    
    # Séparateurs variés pour competences_brut
    separators = [", ", " / ", " • ", "; ", " | ", "\n"]
    sep = random.choice(separators)
    competences_brut = sep.join(selected_comps)
    
    # Description
    template = random.choice(DESCRIPTIONS_TEMPLATES)
    padded = selected_comps + ["Git", "Linux", "Docker", "Python", "SQL"]
    desc = template.format(
        titre=titre,
        comp1=padded[0], comp2=padded[1], comp3=padded[2],
        comp4=padded[3], comp5=padded[4], n=random.randint(3, 15)
    )
    
    # Contrat
    contrat_key = random.choices(list(CONTRAT_VARIANTS.keys()), weights=CONTRAT_WEIGHTS, k=1)[0]
    contrat = random.choice(CONTRAT_VARIANTS[contrat_key])
    
    # Expérience
    experience = random.choice(EXPERIENCE_VARIANTS)
    
    # Salaire
    salaire = random.choice(SALAIRE_VARIANTS)
    
    # Date expiration (parfois incohérente)
    if random.random() < 0.05:  # 5% dates incohérentes
        date_exp = date_pub - timedelta(days=random.randint(1, 30))
    else:
        date_exp = date_pub + timedelta(days=random.randint(15, 60))
    
    # Dates parfois en format différent
    if random.random() < 0.1:
        date_pub_str = date_pub.strftime("%d/%m/%Y")
    else:
        date_pub_str = date_pub.strftime("%Y-%m-%d")
    
    date_exp_str = date_exp.strftime("%Y-%m-%d")
    
    offre = {
        "id_offre": id_offre,
        "source": source,
        "titre_poste": titre,
        "description": desc,
        "competences_brut": competences_brut,
        "entreprise": random.choice(ENTREPRISES),
        "ville": ville,
        "type_contrat": contrat,
        "experience_requise": experience,
        "salaire_brut": salaire,
        "niveau_etudes": random.choice(NIVEAUX_ETUDES),
        "secteur": random.choice(SECTEURS),
        "date_publication": date_pub_str,
        "date_expiration": date_exp_str,
        "nb_postes": random.choices([1, 2, 3, 5], weights=[0.7, 0.15, 0.1, 0.05], k=1)[0],
        "teletravail": random.choice(TELETRAVAIL),
        "langue_requise": random.choice(LANGUES),
    }
    return offre


def generate_referentiel():
    """Génère le référentiel de compétences IT."""
    return {
        "familles": {
            "langages": {
                "python": ["python", "python3", "py"],
                "javascript": ["javascript", "js", "node.js", "nodejs", "node"],
                "java": ["java", "java8", "java11", "java17"],
                "sql": ["sql", "mysql", "postgresql", "postgres", "oracle", "tsql"],
                "r": ["r", "rlang", "r-studio"],
                "typescript": ["typescript", "ts"],
                "scala": ["scala"],
                "c_sharp": ["c#", "csharp", ".net"],
                "php": ["php", "php7", "php8"],
                "go": ["go", "golang"],
                "ruby": ["ruby", "ruby on rails"],
                "swift": ["swift"],
                "kotlin": ["kotlin"],
                "bash": ["bash", "shell", "sh"],
                "html_css": ["html", "css", "html5", "css3"],
            },
            "frameworks_web": {
                "react": ["react", "reactjs", "react.js"],
                "angular": ["angular", "angularjs"],
                "vue": ["vue", "vue.js", "vuejs"],
                "django": ["django", "django rest"],
                "spring": ["spring", "spring boot", "springboot"],
                "flask": ["flask"],
                "express": ["express", "express.js"],
                "laravel": ["laravel"],
                "next": ["next.js", "nextjs"],
                "flutter": ["flutter"],
                "react_native": ["react native"],
            },
            "data_engineering": {
                "spark": ["spark", "apache spark", "pyspark"],
                "kafka": ["kafka", "apache kafka"],
                "airflow": ["airflow", "apache airflow"],
                "dbt": ["dbt", "data build tool"],
                "hadoop": ["hadoop", "hdfs", "mapreduce"],
                "etl": ["etl"],
                "pandas": ["pandas"],
                "numpy": ["numpy"],
            },
            "cloud": {
                "aws": ["aws", "amazon web services", "ec2", "s3", "lambda"],
                "gcp": ["gcp", "google cloud", "bigquery", "cloud storage"],
                "azure": ["azure", "microsoft azure", "synapse"],
            },
            "bi_analytics": {
                "power_bi": ["power bi", "powerbi", "pbi"],
                "tableau": ["tableau", "tableau desktop"],
                "metabase": ["metabase"],
                "looker": ["looker", "looker studio"],
                "excel": ["excel", "microsoft excel"],
                "jupyter": ["jupyter", "jupyter notebook"],
            },
            "devops_infra": {
                "docker": ["docker", "dockerfile", "docker-compose"],
                "kubernetes": ["kubernetes", "k8s"],
                "jenkins": ["jenkins"],
                "terraform": ["terraform"],
                "ansible": ["ansible"],
                "ci_cd": ["ci/cd", "cicd", "continuous integration"],
                "git": ["git", "github", "gitlab"],
                "linux": ["linux", "ubuntu", "centos", "debian"],
            },
            "databases": {
                "postgresql": ["postgresql", "postgres"],
                "mysql": ["mysql"],
                "mongodb": ["mongodb", "mongo"],
                "redis": ["redis"],
                "elasticsearch": ["elasticsearch", "elastic"],
                "oracle_db": ["oracle"],
                "firebase": ["firebase"],
            },
            "data_science_ml": {
                "machine_learning": ["machine learning", "ml"],
                "deep_learning": ["deep learning", "dl"],
                "tensorflow": ["tensorflow", "tf"],
                "pytorch": ["pytorch"],
                "scikit_learn": ["scikit-learn", "sklearn"],
                "nlp": ["nlp", "natural language processing"],
                "computer_vision": ["computer vision", "cv", "opencv"],
            },
            "methodologies": {
                "agile": ["agile", "méthode agile"],
                "scrum": ["scrum"],
                "jira": ["jira"],
                "uml": ["uml"],
                "design_patterns": ["design patterns"],
            },
            "securite": {
                "firewall": ["firewall"],
                "siem": ["siem"],
                "pentest": ["pentest", "penetration testing"],
                "iso_27001": ["iso 27001", "iso27001"],
            },
            "autres": {
                "rest_api": ["rest api", "api rest", "restful"],
                "microservices": ["microservices", "micro-services"],
                "figma": ["figma"],
                "networking": ["networking", "réseau", "tcp/ip"],
            },
        }
    }


def generate_entreprises_csv():
    """Génère le fichier CSV des entreprises IT au Maroc."""
    rows = [
        "nom_entreprise,secteur,taille,ville_siege,site_web,type",
    ]
    types_e = ["SSII", "Produit", "Conseil", "Telecom", "Banque", "Autre"]
    tailles = ["PME", "ETI", "Grande Entreprise", "Startup"]
    for ent in ENTREPRISES:
        ville = random.choice(list(VILLES_VARIANTS.keys()))
        t = random.choice(types_e)
        taille = random.choice(tailles)
        site = "https://www." + ent.lower().replace(" ", "").replace("é","e") + ".ma"
        rows.append(f"{ent},{random.choice(SECTEURS)},{taille},{ville},{site},{t}")
    return "\n".join(rows)


def main():
    """Point d'entrée principal."""
    output_dir = os.path.dirname(os.path.abspath(__file__)) + "/raw"
    os.makedirs(output_dir, exist_ok=True)

    # Générer les offres
    print("Génération de 5000 offres d'emploi IT...")
    offres = []
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2024, 11, 30)
    delta = (end_date - start_date).days

    for i in range(5000):
        date_pub = start_date + timedelta(days=random.randint(0, delta))
        offres.append(generate_offre(i, date_pub))

    # Sauvegarder
    filepath = os.path.join(output_dir, "offres_emploi_it_maroc.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump({"offres": offres}, f, ensure_ascii=False, indent=2)
    print(f"[OK] {len(offres)} offres sauvegardees dans {filepath}")

    # Référentiel
    ref_path = os.path.join(output_dir, "referentiel_competences_it.json")
    with open(ref_path, "w", encoding="utf-8") as f:
        json.dump(generate_referentiel(), f, ensure_ascii=False, indent=2)
    print(f"[OK] Referentiel sauvegarde dans {ref_path}")

    # Entreprises
    csv_path = os.path.join(output_dir, "entreprises_it_maroc.csv")
    with open(csv_path, "w", encoding="utf-8") as f:
        f.write(generate_entreprises_csv())
    print(f"[OK] Entreprises sauvegardees dans {csv_path}")


if __name__ == "__main__":
    main()
