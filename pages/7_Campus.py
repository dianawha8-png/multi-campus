import streamlit as st
import plotly.express as px
from services.supabase_client import get_client
from services import stats_service as stats
from services.export_service import vers_excel, vers_csv

st.set_page_config(page_title="Campus", page_icon="🏢", layout="wide")
st.title("🏢 Campus")

client = get_client()
df = stats.moyenne_par_campus(client)

st.caption(f"{len(df)} campus")

if not df.empty:
    fig = px.bar(df, x="campus_texte", y="nb_notes", color="campus_texte",
                 labels={"campus_texte": "Campus", "nb_notes": "Nombre de notes"})
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(df, use_container_width=True)
    c1, c2 = st.columns(2)
    c1.download_button("⬇️ Excel", vers_excel(df, "Campus"), "campus.xlsx")
    c2.download_button("⬇️ CSV", vers_csv(df), "campus.csv", "text/csv")
else:
    st.info("Aucune donnée de campus disponible.")
