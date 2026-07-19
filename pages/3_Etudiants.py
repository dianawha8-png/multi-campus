import streamlit as st
from services.supabase_client import get_client
from services.export_service import vers_excel, vers_csv

st.set_page_config(page_title="Étudiants", page_icon="👨‍🎓", layout="wide")
st.title("👨‍🎓 Étudiants")

client = get_client()

col1, col2 = st.columns(2)
classe_filtre = col1.text_input("Filtrer par classe")
campus_filtre = col2.selectbox("Filtrer par campus", ["", "PLATEAU", "YOPOUGON", "YAMOUSSOUKRO"])

q = client.table("v_etudiants").select("*")
if classe_filtre:
    q = q.ilike("classe_texte", f"%{classe_filtre}%")
if campus_filtre:
    q = q.eq("campus_texte", campus_filtre)
res = q.execute()

import pandas as pd
df = pd.DataFrame(res.data)
st.caption(f"{len(df)} étudiant(s)")

if not df.empty:
    st.dataframe(df.sort_values("nom"), use_container_width=True, height=550)
    c1, c2 = st.columns(2)
    c1.download_button("⬇️ Excel", vers_excel(df, "Etudiants"), "etudiants.xlsx")
    c2.download_button("⬇️ CSV", vers_csv(df), "etudiants.csv", "text/csv")
else:
    st.info("Aucun étudiant trouvé.")
