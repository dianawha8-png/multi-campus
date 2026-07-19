import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder

from services.supabase_client import get_client
from services import stats_service as stats
from services.export_service import vers_excel, vers_csv, vers_pdf

st.set_page_config(page_title="Notes centrales", page_icon="📋", layout="wide")
st.title("📋 Notes centrales")

client = get_client()

with st.expander("🔎 Recherche", expanded=True):
    c1, c2, c3 = st.columns(3)
    matricule = c1.text_input("Matricule")
    nom = c2.text_input("Nom")
    prenoms = c3.text_input("Prénoms")
    c4, c5, c6 = st.columns(3)
    classe = c4.text_input("Classe")
    ue = c5.text_input("UE")
    campus = c6.selectbox("Campus", ["", "PLATEAU", "YOPOUGON", "YAMOUSSOUKRO"])

df = stats.recherche_notes(
    client, matricule=matricule, nom=nom, prenoms=prenoms,
    classe=classe, ue=ue, campus=campus,
)

st.caption(f"{len(df)} résultat(s)")

if not df.empty:
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=25)
    gb.configure_default_column(filterable=True, sortable=True, resizable=True)
    AgGrid(df, gridOptions=gb.build(), height=500, theme="balham")

    st.divider()
    st.subheader("Export")
    e1, e2, e3 = st.columns(3)
    e1.download_button("⬇️ Excel", vers_excel(df, "Notes"), "notes_centrales.xlsx",
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    e2.download_button("⬇️ CSV", vers_csv(df), "notes_centrales.csv", "text/csv")
    e3.download_button("⬇️ PDF", vers_pdf(df, "Notes centrales"), "notes_centrales.pdf", "application/pdf")
else:
    st.info("Aucune donnée. Affinez ou réinitialisez les filtres, ou importez des fichiers.")
