"""
Connexion centralisée à Supabase — compatible avec les nouvelles clés API
2026 (sb_publishable_..., sb_secret_...) et les anciennes clés JWT
(anon / service_role) pour compatibilité ascendante.

IMPORTANT :
- Cette application écrit dans Supabase (import Excel, mise à jour des
  notes) : elle doit utiliser une clé côté SERVEUR, c'est-à-dire
  sb_secret_... (nouveau format) ou service_role (ancien format JWT).
  N'utilisez jamais sb_publishable_... ou anon ici : les écritures
  échoueraient silencieusement ou seraient bloquées selon vos politiques RLS.
- Nécessite supabase>=2.10 (voir requirements.txt). Les versions du client
  antérieures à l'introduction des nouvelles clés (mi-2025) peuvent renvoyer
  "Invalid API key" même avec une clé sb_secret_... valide.
"""
import os
import re

import streamlit as st
from supabase import create_client, Client

# Formats de clés reconnus, à titre indicatif pour le diagnostic
_PREFIXES_SERVEUR = ("sb_secret_",)
_PREFIXES_CLIENT = ("sb_publishable_",)
_JWT_RE = re.compile(r"^eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$")


@st.cache_resource(show_spinner=False)
def get_client() -> Client:
    """Retourne un client Supabase mis en cache pour toute la session serveur."""
    url = _nettoyer(_get_config("SUPABASE_URL"))
    key = _nettoyer(_get_config("SUPABASE_KEY"))

    if not url or not key:
        st.error(
            "Configuration Supabase manquante. Renseignez SUPABASE_URL et "
            "SUPABASE_KEY dans les secrets Streamlit (Settings > Secrets) ou "
            "dans le fichier .env pour une exécution locale."
        )
        st.stop()

    _diagnostiquer_cle(url, key)

    try:
        return create_client(url, key)
    except Exception as exc:
        st.error(
            "Impossible d'initialiser le client Supabase. "
            f"Détail technique : {exc}"
        )
        st.stop()


def _nettoyer(valeur: str | None) -> str | None:
    """Supprime les espaces, retours à la ligne et guillemets accidentels
    (source fréquente de 'Invalid API key' lors d'un copier-coller dans
    Streamlit Secrets ou un fichier .env)."""
    if valeur is None:
        return None
    return valeur.strip().strip('"').strip("'")


def _get_config(name: str) -> str | None:
    """Lit une variable de config depuis st.secrets, sinon depuis l'environnement."""
    try:
        if name in st.secrets:
            return st.secrets[name]
    except Exception:
        pass
    return os.environ.get(name)


def _diagnostiquer_cle(url: str, key: str) -> None:
    """Avertit dans l'interface si la clé fournie n'est probablement pas la
    bonne, sans bloquer l'exécution (Supabase reste seul juge final)."""
    if not url.startswith("https://") or ".supabase.co" not in url:
        st.warning(
            "SUPABASE_URL ne ressemble pas à une URL de projet Supabase "
            "valide (attendu : https://xxxxxxxx.supabase.co)."
        )

    est_secret_nouveau = key.startswith(_PREFIXES_SERVEUR)
    est_publishable_nouveau = key.startswith(_PREFIXES_CLIENT)
    est_jwt_legacy = bool(_JWT_RE.match(key))

    if est_publishable_nouveau:
        st.warning(
            "La clé fournie est une clé sb_publishable_... (clé client, "
            "publique). Cette application écrit dans la base et a besoin "
            "d'une clé serveur : utilisez la clé sb_secret_... visible dans "
            "Supabase Dashboard > Project Settings > API Keys > Secret keys."
        )
    elif not (est_secret_nouveau or est_jwt_legacy):
        st.warning(
            "Le format de SUPABASE_KEY n'est pas reconnu (ni sb_secret_..., "
            "ni clé JWT legacy commençant par eyJ...). Vérifiez qu'aucun "
            "caractère n'a été tronqué ou ajouté lors du copier-coller."
        )
