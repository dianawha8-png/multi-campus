import os
import streamlit as st
from supabase import create_client

@st.cache_resource
def get_client():
    url = st.secrets.get("SUPABASE_URL") or os.getenv("SUPABASE_URL")
    key = st.secrets.get("SUPABASE_KEY") or os.getenv("SUPABASE_KEY")

    return create_client(
        url.strip(),
        key.strip()
    )
