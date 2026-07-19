# Gestion des Notes — Multi-Campus

Application web de consolidation des notes (PLATEAU, YOPOUGON, YAMOUSSOUKRO —
BTS, Licence, Master), accessible uniquement via une URL de navigateur.

Voir `ARCHITECTURE.md` pour le détail de l'architecture.

## 1. Créer le projet Supabase

1. Allez sur https://supabase.com → **New project**.
2. Choisissez un nom, un mot de passe de base de données, une région proche
   (Europe de préférence).
3. Une fois le projet créé, ouvrez **SQL Editor > New query**, collez le
   contenu de `sql/schema.sql`, puis cliquez sur **Run**. Toutes les tables,
   contraintes, index et vues sont créées.
4. Dans **Project Settings > API**, récupérez :
   - `Project URL` → variable `SUPABASE_URL`
   - `service_role` key (⚠️ jamais exposée publiquement, uniquement utilisée
     côté serveur Streamlit) → variable `SUPABASE_KEY`

## 2. Exécution locale (optionnel, pour tester avant déploiement)

```bash
python -m venv .venv
source .venv/bin/activate        # Windows : .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# éditez .env et renseignez SUPABASE_URL / SUPABASE_KEY

streamlit run app.py
```

L'application s'ouvre sur `http://localhost:8501`.

## 3. Déploiement sur Streamlit Cloud (recommandé — gratuit)

1. Poussez ce projet sur un dépôt GitHub (public ou privé).
2. Allez sur https://share.streamlit.io → **New app**.
3. Sélectionnez le dépôt, la branche, et `app.py` comme fichier principal.
4. Dans **Advanced settings > Secrets**, collez le contenu de
   `.streamlit/secrets.toml.example` en remplaçant par vos vraies valeurs :
   ```toml
   SUPABASE_URL = "https://xxxxxxxxxxxxx.supabase.co"
   SUPABASE_KEY = "votre-cle-service-role"
   ```
5. Cliquez sur **Deploy**. Une URL publique est générée
   (`https://votre-app.streamlit.app`) — c'est le seul lien à partager avec
   les utilisateurs, aucune installation n'est requise côté poste client.

## 4. Déploiement alternatif — Render

1. Créez un **Web Service** sur https://render.com, connecté à votre dépôt.
2. Build command : `pip install -r requirements.txt`
3. Start command :
   ```bash
   streamlit run app.py --server.port $PORT --server.address 0.0.0.0
   ```
4. Dans **Environment**, ajoutez `SUPABASE_URL` et `SUPABASE_KEY`.
5. Déployez : Render fournit une URL `https://votre-app.onrender.com`.

## 5. Déploiement alternatif — Railway

1. Créez un nouveau projet sur https://railway.app à partir du dépôt GitHub.
2. Railway détecte Python automatiquement ; ajoutez un fichier `Procfile` à
   la racine si besoin :
   ```
   web: streamlit run app.py --server.port $PORT --server.address 0.0.0.0
   ```
3. Dans **Variables**, ajoutez `SUPABASE_URL` et `SUPABASE_KEY`.
4. Déployez : Railway fournit une URL publique.

## 6. Convention de nommage des fichiers Excel importés

```
CAMPUS-SEMESTRE-ENSEIGNANT.xlsx
```
Exemples : `ABIDJAN-S1-KOUADIO.xlsx`, `YOPOUGON-S4-YAO.xlsx`

Chaque feuille du classeur = une classe. Colonnes attendues dans chaque
tableau : `MATRICULE, NOM, PRENOMS, CLASSE, UE, CAMPUS, NOTE1, NOTE2, MOYENNE`.

## 7. Structure du projet

Voir `ARCHITECTURE.md` section 3.

## 8. Support / évolutions prévues

- Page **Paramètres** : gestion des campus et formations, test de connexion.
- Authentification utilisateurs (email/mot de passe Supabase Auth) activable
  en ajoutant du RLS par utilisateur — non incluse dans cette première
  version pour rester simple à déployer.
