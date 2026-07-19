# Architecture — Application de Consolidation des Notes Multi-Campus

## 1. Vue d'ensemble

Application web 100% navigateur, sans installation côté utilisateur (pas de Node.js,
pas de PostgreSQL local, pas de Docker). Stack :

```
┌─────────────────────────────────────────────────────────────┐
│                     NAVIGATEUR (utilisateur)                  │
│                 https://votre-app.streamlit.app               │
└───────────────────────────┬────────────────────────────────┘
                             │ HTTPS
┌───────────────────────────▼────────────────────────────────┐
│              STREAMLIT CLOUD / RENDER / RAILWAY               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  app.py  (point d'entrée + navigation multipage)        │  │
│  │  pages/                                                  │  │
│  │    0_Tableau_de_Bord.py                                  │  │
│  │    1_Import_Excel.py                                     │  │
│  │    2_Notes_Centrales.py                                  │  │
│  │    3_Etudiants.py                                        │  │
│  │    4_Enseignants.py                                      │  │
│  │    5_UE.py                                                │  │
│  │    6_Classes.py                                           │  │
│  │    7_Campus.py                                            │  │
│  │    8_Rapports.py                                          │  │
│  │    9_Parametres.py                                        │  │
│  │  services/                                                │  │
│  │    supabase_client.py   (connexion + requêtes)            │  │
│  │    excel_import.py      (lecture Excel, parsing, anti-doublon)│
│  │    stats_service.py     (agrégations, classements)        │  │
│  │    export_service.py    (Excel / CSV / PDF)                │  │
│  │    validation.py        (détection erreurs)                │  │
│  └───────────────────────────────────┬─────────────────────┘  │
└────────────────────────────────────────┼────────────────────┘
                                          │ HTTPS (API REST + clé)
┌─────────────────────────────────────────▼────────────────────┐
│                          SUPABASE                               │
│   PostgreSQL managé + API REST auto-générée + Auth (option)     │
│   Tables : notes_centrales, etudiants, enseignants, ue,          │
│            classes, campus, fichiers_import, journal_erreurs     │
└───────────────────────────────────────────────────────────────┘
```

## 2. Pourquoi cette stack

- **Streamlit** : UI Python pure, hébergeable gratuitement sur Streamlit Cloud,
  aucun build front-end, aucune installation côté utilisateur final (juste un lien).
- **Supabase** : PostgreSQL managé + API REST + tableau de bord d'administration,
  gratuit jusqu'à un volume confortable, aucune installation de base de données.
- **Pandas / OpenPyXL** : lecture/écriture Excel côté serveur uniquement.
- **Streamlit AgGrid** : grilles interactives (tri, filtre, édition) pour Notes
  Centrales, Étudiants, etc.
- **Plotly** : graphiques du tableau de bord et des rapports.

## 3. Arborescence du projet

```
gestion-notes/
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
├── .streamlit/
│   └── config.toml
├── services/
│   ├── __init__.py
│   ├── supabase_client.py
│   ├── excel_import.py
│   ├── stats_service.py
│   ├── export_service.py
│   └── validation.py
├── pages/
│   ├── 0_Tableau_de_Bord.py
│   ├── 1_Import_Excel.py
│   ├── 2_Notes_Centrales.py
│   ├── 3_Etudiants.py
│   ├── 4_Enseignants.py
│   ├── 5_UE.py
│   ├── 6_Classes.py
│   ├── 7_Campus.py
│   ├── 8_Rapports.py
│   └── 9_Parametres.py
├── sql/
│   └── schema.sql
└── README.md
```

## 4. Flux fonctionnel (Import → Consolidation)

1. L'utilisateur dépose un ou plusieurs fichiers `.xlsx` sur la page **Import Excel**.
2. `excel_import.py` ouvre chaque fichier avec `openpyxl`, parcourt **toutes les
   feuilles**, détecte le tableau structuré de chaque feuille et extrait les lignes
   avec `pandas`.
3. Pour chaque ligne : extraction du campus (depuis le nom du fichier ou la colonne
   CAMPUS), du semestre (depuis le nom du fichier, ex: `S1`), de la classe (nom de
   la feuille), calcul de la `cle_import` (`matricule|nom|prenoms|classe` ou
   `*|nom|prenoms|classe` si matricule vide).
4. Validation : lignes vides, matricule absent (toléré mais signalé), colonnes
   manquantes, feuille vide, fichier vide → tout est journalisé dans
   `journal_erreurs` et affiché à l'écran avant import.
5. Anti-doublon : recherche de `cle_import` dans `notes_centrales`.
   - Existe → `UPDATE` (met à jour notes, moyenne, date de modification).
   - N'existe pas → `INSERT`.
6. Le fichier source est journalisé dans `fichiers_import` (nom, date, nb lignes,
   nb erreurs) pour traçabilité.
7. Les pages Notes Centrales / Étudiants / Enseignants / UE / Classes / Campus
   affichent des vues filtrées de la même table centrale via des `VIEW` SQL.
8. Rapports et Tableau de bord agrègent via des requêtes Supabase (ou vues SQL)
   et affichent avec Plotly / AgGrid, avec export Excel / CSV / PDF.

## 5. Sécurité & configuration

- Les identifiants Supabase (`SUPABASE_URL`, `SUPABASE_KEY`) sont stockés en
  variables d'environnement / `st.secrets`, jamais en dur dans le code.
- Utilisation de la clé `service_role` uniquement côté serveur Streamlit (jamais
  exposée au navigateur, car Streamlit exécute tout côté serveur).
- Row Level Security (RLS) activable sur Supabase si authentification multi-
  utilisateurs est ajoutée plus tard (prévu en page Paramètres).

## 6. Étapes suivantes

- Étape 2 : script SQL Supabase complet (tables, contraintes, index, vues).
- Étape 3 : code Streamlit (app.py + pages).
- Étape 4 : service d'import Excel complet.
- Étape 5 : tableau de bord et rapports.
