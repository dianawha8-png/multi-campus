import streamlit as st
import plotly.express as px

from services.supabase_client import get_client
from services import stats_service as stats

st.set_page_config(page_title="Tableau de bord", page_icon="📊", layout="wide")
st.title("📊 Tableau de bord")

client = get_client()

# ----- Compteurs -----
donnees = stats.tableau_de_bord(client)

c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Étudiants", donnees.get("nb_etudiants", 0))
c2.metric("Notes importées", donnees.get("nb_notes", 0))
c3.metric("Enseignants", donnees.get("nb_enseignants", 0))
c4.metric("UE", donnees.get("nb_ue", 0))
c5.metric("Classes", donnees.get("nb_classes", 0))
c6.metric("Campus", donnees.get("nb_campus", 0))

st.divider()

col_gauche, col_droite = st.columns(2)

with col_gauche:
    st.subheader("Moyenne par campus")
    df_campus = stats.moyenne_par_campus(client)
    if not df_campus.empty:
        fig = px.bar(df_campus, x="campus_texte", y="moyenne", color="campus_texte",
                     text="moyenne", labels={"campus_texte": "Campus", "moyenne": "Moyenne"})
        fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aucune donnée disponible. Importez des fichiers Excel.")

with col_droite:
    st.subheader("Moyenne par classe")
    df_classe = stats.moyenne_par_classe(client)
    if not df_classe.empty:
        fig = px.bar(df_classe.sort_values("moyenne", ascending=True),
                     x="moyenne", y="classe_texte", color="campus_texte", orientation="h",
                     labels={"classe_texte": "Classe", "moyenne": "Moyenne"})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aucune donnée disponible.")

st.divider()

col_gauche2, col_droite2 = st.columns(2)

with col_gauche2:
    st.subheader("Moyenne par UE (top 15)")
    df_ue = stats.moyenne_par_ue(client)
    if not df_ue.empty:
        df_ue = df_ue.sort_values("nb_notes", ascending=False).head(15)
        fig = px.bar(df_ue, x="ue", y="moyenne", text="moyenne")
        fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
        fig.update_layout(xaxis_tickangle=-40)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aucune donnée disponible.")

with col_droite2:
    st.subheader("Répartition des notes saisies par enseignant")
    df_ens = stats.moyenne_par_enseignant(client)
    if not df_ens.empty:
        fig = px.pie(df_ens, names="enseignant", values="nb_notes_saisies", hole=0.4)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aucune donnée disponible.")

st.divider()
st.subheader("⚠️ Points de vigilance")
v1, v2 = st.columns(2)
with v1:
    df_sans_matricule = stats.etudiants_sans_matricule(client)
    st.metric("Lignes sans matricule", len(df_sans_matricule))
with v2:
    df_sans_note = stats.etudiants_sans_note(client)
    st.metric("Lignes sans aucune note", len(df_sans_note))
