import streamlit as st
from services.supabase_client import get_client
from services import stats_service as stats
from services.export_service import vers_excel, vers_csv, vers_pdf

st.set_page_config(page_title="Rapports", page_icon="🧾", layout="wide")
st.title("🧾 Rapports")

client = get_client()

onglet1, onglet2, onglet3 = st.tabs(["Classement général", "Anomalies", "Historique des imports"])

with onglet1:
    st.subheader("Classement des étudiants")
    df = stats.classement_etudiants(client)
    if not df.empty:
        st.dataframe(df, use_container_width=True, height=500)
        c1, c2, c3 = st.columns(3)
        c1.download_button("⬇️ Excel", vers_excel(df, "Classement"), "classement.xlsx")
        c2.download_button("⬇️ CSV", vers_csv(df), "classement.csv", "text/csv")
        c3.download_button("⬇️ PDF", vers_pdf(df, "Classement des étudiants"), "classement.pdf", "application/pdf")
    else:
        st.info("Aucune donnée disponible.")

with onglet2:
    st.subheader("Étudiants sans matricule")
    df_sm = stats.etudiants_sans_matricule(client)
    st.dataframe(df_sm, use_container_width=True)

    st.subheader("Étudiants sans note")
    df_sn = stats.etudiants_sans_note(client)
    st.dataframe(df_sn, use_container_width=True)

with onglet3:
    st.subheader("Historique des fichiers importés")
    res = client.table("fichiers_import").select("*").order("date_import", desc=True).execute()
    import pandas as pd
    df_hist = pd.DataFrame(res.data)
    st.dataframe(df_hist, use_container_width=True, height=400)

    st.subheader("Journal des erreurs")
    res_err = client.table("journal_erreurs").select("*").order("date_creation", desc=True).limit(500).execute()
    df_err = pd.DataFrame(res_err.data)
    st.dataframe(df_err, use_container_width=True, height=400)
