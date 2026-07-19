import streamlit as st
import pandas as pd
from services.supabase_client import get_client
from services.export_service import vers_excel, vers_csv

st.set_page_config(page_title="Enseignants", page_icon="👩‍🏫", layout="wide")
st.title("👩‍🏫 Enseignants")

client = get_client()
res = client.table("v_enseignants").select("*").execute()
df = pd.DataFrame(res.data)

st.caption(f"{len(df)} enseignant(s)")

if not df.empty:
    st.dataframe(df.sort_values("enseignant"), use_container_width=True, height=550)
    c1, c2 = st.columns(2)
    c1.download_button("⬇️ Excel", vers_excel(df, "Enseignants"), "enseignants.xlsx")
    c2.download_button("⬇️ CSV", vers_csv(df), "enseignants.csv", "text/csv")
else:
    st.info("Aucun enseignant trouvé. L'enseignant est déduit du nom de fichier importé.")
