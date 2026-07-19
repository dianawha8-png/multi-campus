import streamlit as st
import pandas as pd
from services.supabase_client import get_client
from services.export_service import vers_excel, vers_csv

st.set_page_config(page_title="UE", page_icon="📚", layout="wide")
st.title("📚 Unités d'enseignement")

client = get_client()
res = client.table("v_moyenne_par_ue").select("*").execute()
df = pd.DataFrame(res.data)

st.caption(f"{len(df)} UE")

if not df.empty:
    st.dataframe(df.sort_values("ue"), use_container_width=True, height=550)
    c1, c2 = st.columns(2)
    c1.download_button("⬇️ Excel", vers_excel(df, "UE"), "ue.xlsx")
    c2.download_button("⬇️ CSV", vers_csv(df), "ue.csv", "text/csv")
else:
    st.info("Aucune UE trouvée.")
