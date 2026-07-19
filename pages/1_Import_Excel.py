import streamlit as st
import pandas as pd

from services.supabase_client import get_client
from services.validation import RapportValidation
from services.excel_import import (
    extraire_lignes_fichier, importer_lignes_supabase,
    journaliser_import, parser_nom_fichier,
)

st.set_page_config(page_title="Import Excel", page_icon="📥", layout="wide")
st.title("📥 Import Excel")

st.markdown(
    "Déposez un ou plusieurs fichiers Excel (`.xlsx`). "
    "Convention de nom recommandée : `CAMPUS-SEMESTRE-ENSEIGNANT.xlsx` "
    "(ex : `ABIDJAN-S1-KOUADIO.xlsx`)."
)

fichiers = st.file_uploader(
    "Fichiers Excel", type=["xlsx"], accept_multiple_files=True
)

if fichiers:
    if st.button("🔍 Analyser les fichiers", type="primary"):
        client = get_client()
        rapport_global = RapportValidation()
        toutes_lignes_par_fichier = {}

        with st.spinner("Lecture des fichiers en cours..."):
            for f in fichiers:
                contenu = f.read()
                if not contenu:
                    rapport_global.ajouter(f.name, "-", 0, "fichier_vide", "Fichier vide")
                    continue
                lignes, nb_feuilles = extraire_lignes_fichier(f.name, contenu, rapport_global)
                toutes_lignes_par_fichier[f.name] = (lignes, nb_feuilles)

        st.session_state["import_lignes"] = toutes_lignes_par_fichier
        st.session_state["import_rapport"] = rapport_global

if "import_lignes" in st.session_state:
    toutes_lignes_par_fichier = st.session_state["import_lignes"]
    rapport_global = st.session_state["import_rapport"]

    total_lignes = sum(len(l) for l, _ in toutes_lignes_par_fichier.values())
    st.success(f"{len(toutes_lignes_par_fichier)} fichier(s) analysé(s) — {total_lignes} ligne(s) valide(s) détectée(s).")

    if rapport_global.nb_erreurs:
        st.warning(f"{rapport_global.nb_erreurs} anomalie(s) détectée(s).")
        with st.expander("Voir le détail des anomalies"):
            df_erreurs = pd.DataFrame([{
                "Fichier": e.nom_fichier, "Feuille": e.feuille,
                "Ligne Excel": e.ligne_excel, "Type": e.type_erreur, "Détail": e.detail,
            } for e in rapport_global.erreurs])
            st.dataframe(df_erreurs, use_container_width=True, height=300)

    with st.expander("Aperçu des lignes qui seront importées", expanded=True):
        for nom_fichier, (lignes, nb_feuilles) in toutes_lignes_par_fichier.items():
            st.markdown(f"**{nom_fichier}** — {nb_feuilles} feuille(s) lue(s), {len(lignes)} ligne(s)")
            if lignes:
                st.dataframe(pd.DataFrame(lignes).head(20), use_container_width=True)

    st.divider()
    if st.button("✅ Confirmer l'import dans Supabase", type="primary"):
        client = get_client()
        resume_total = {"inserees": 0, "mises_a_jour": 0, "erreurs_supabase": 0}
        barre = st.progress(0.0)
        fichiers_list = list(toutes_lignes_par_fichier.items())

        for i, (nom_fichier, (lignes, nb_feuilles)) in enumerate(fichiers_list):
            if lignes:
                resume = importer_lignes_supabase(client, lignes)
                infos_fichier = parser_nom_fichier(nom_fichier)
                journaliser_import(client, nom_fichier, infos_fichier, resume, nb_feuilles, rapport_global)
                for k in resume_total:
                    resume_total[k] += resume.get(k, 0)
            barre.progress((i + 1) / len(fichiers_list))

        st.success(
            f"Import terminé : {resume_total['inserees']} ligne(s) créée(s), "
            f"{resume_total['mises_a_jour']} ligne(s) mise(s) à jour, "
            f"{resume_total['erreurs_supabase']} erreur(s) d'écriture."
        )
        del st.session_state["import_lignes"]
        del st.session_state["import_rapport"]
