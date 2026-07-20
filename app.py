"""
Application de consolidation des notes multi-campus.
Point d'entrée Streamlit — configure la page et affiche l'accueil.
Les autres écrans sont dans pages/ (navigation automatique multipage Streamlit).
"""
import streamlit as st

st.set_page_config(
    page_title="Gestion des Notes — Multi-Campus",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🎓 Consolidation des Notes — Multi-Campus")
st.caption("PLATEAU · YOPOUGON · YAMOUSSOUKRO — BTS · Licence · Master")

st.markdown("""
Bienvenue. Utilisez le menu à gauche pour naviguer :

| Page | Description |
|---|---|
| **Tableau de bord** | Vue d'ensemble, compteurs et graphiques |
| **Import Excel** | Déposer les fichiers des enseignants |
| **Notes centrales** | Recherche et consultation de toutes les notes |
| **Étudiants** | Vue consolidée par étudiant |
| **Enseignants** | Vue consolidée par enseignant |
| **UE** | Vue consolidée par unité d'enseignement |
| **Classes** | Vue consolidée par classe |
| **Campus** | Vue consolidée par campus |
| **Rapports** | Statistiques, classements et exports |
| **Paramètres** | Campus, formations, connexion Supabase |
""")

def _check_connexion() -> bool:
    try:
        from services.supabase_client import get_client
        get_client()
        return True
    except Exception:
        return False


with st.sidebar:
    st.success("Connecté à Supabase" if _check_connexion() else "Non connecté")
