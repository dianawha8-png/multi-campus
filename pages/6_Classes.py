import streamlit as st
import pandas as pd
from services.supabase_client import get_client
from services import stats_service as stats
from services.export_service import vers_excel, vers_csv

st.set_page_config(page_title="Classes", page_icon="🏫", layout="wide")
st.title("🏫 Classes")

client = get_client()
df = stats.moyenne_par_classe(client)

st.caption(f"{len(df)} classe(s)")

if not df.empty:
    st.dataframe(df.sort_values("classe_texte"), use_container_width=True, height=400)
    c1, c2 = st.columns(2)
    c1.download_button("⬇️ Excel", vers_excel(df, "Classes"), "classes.xlsx")
    c2.download_button("⬇️ CSV", vers_csv(df), "classes.csv", "text/csv")

    st.divider()
    st.subheader("Classement des étudiants d'une classe")
    classe_choisie = st.selectbox("Choisir une classe", df["classe_texte"].sort_values().unique())
    if classe_choisie:
        classement = stats.classement_etudiants(client, classe_choisie)
        st.dataframe(classement, use_container_width=True, height=400)
else:
    st.info("Aucune classe trouvée.")
