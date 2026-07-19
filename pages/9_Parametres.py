import streamlit as st
import pandas as pd
from services.supabase_client import get_client

st.set_page_config(page_title="Paramètres", page_icon="⚙️", layout="wide")
st.title("⚙️ Paramètres")

client = get_client()

st.subheader("Connexion Supabase")
try:
    client.table("notes_centrales").select("id").limit(1).execute()
    st.success("Connexion Supabase opérationnelle.")
except Exception as exc:
    st.error(f"Connexion Supabase impossible : {exc}")

st.divider()
st.subheader("Campus")
res = client.table("parametres_campus").select("*").execute()
st.dataframe(pd.DataFrame(res.data), use_container_width=True)

nouveau_campus = st.text_input("Ajouter un campus")
if st.button("Ajouter le campus") and nouveau_campus:
    client.table("parametres_campus").insert({"nom": nouveau_campus.strip().upper()}).execute()
    st.rerun()

st.divider()
st.subheader("Formations")
res_f = client.table("parametres_formations").select("*").execute()
st.dataframe(pd.DataFrame(res_f.data), use_container_width=True)

nouvelle_formation = st.text_input("Ajouter une formation")
if st.button("Ajouter la formation") and nouvelle_formation:
    client.table("parametres_formations").insert({"nom": nouvelle_formation.strip().upper()}).execute()
    st.rerun()
