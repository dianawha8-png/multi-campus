"""
Connexion centralisée à Supabase.
Utilise st.secrets en priorité (Streamlit Cloud) puis les variables d'environnement
(Render / Railway / exécution locale).
"""
import os
import streamlit as st
from supabase import create_client, Client


@st.cache_resource(show_spinner=False)
def get_client() -> Client:
    """Retourne un client Supabase mis en cache pour toute la session serveur."""
    url = _get_config("SUPABASE_URL")
    key = _get_config("SUPABASE_KEY")

    if not url or not key:
        st.error(
            "Configuration Supabase manquante. "
            "Renseignez SUPABASE_URL et SUPABASE_KEY dans les secrets Streamlit "
            "ou dans le fichier .env."
        )
        st.stop()

    return create_client(url, key)


def _get_config(name: str) -> str | None:
    """Lit une variable de config depuis st.secrets, sinon depuis l'environnement."""
    try:
        if name in st.secrets:
            return st.secrets[name]
    except Exception:
        pass
    return os.environ.get(name)
