"""
Requêtes de statistiques et de tableau de bord, appuyées sur les vues SQL
créées dans sql/schema.sql.
"""
import pandas as pd


def tableau_de_bord(client) -> dict:
    res = client.table("v_tableau_de_bord").select("*").execute()
    if res.data:
        return res.data[0]
    return {
        "nb_etudiants": 0, "nb_notes": 0, "nb_enseignants": 0,
        "nb_ue": 0, "nb_classes": 0, "nb_campus": 0,
    }


def moyenne_par_classe(client) -> pd.DataFrame:
    res = client.table("v_moyenne_par_classe").select("*").execute()
    return pd.DataFrame(res.data)


def moyenne_par_ue(client) -> pd.DataFrame:
    res = client.table("v_moyenne_par_ue").select("*").execute()
    return pd.DataFrame(res.data)


def moyenne_par_campus(client) -> pd.DataFrame:
    res = client.table("v_moyenne_par_campus").select("*").execute()
    return pd.DataFrame(res.data)


def moyenne_par_enseignant(client) -> pd.DataFrame:
    res = client.table("v_enseignants").select("*").execute()
    return pd.DataFrame(res.data)


def etudiants_sans_matricule(client) -> pd.DataFrame:
    res = client.table("v_etudiants_sans_matricule").select("*").execute()
    return pd.DataFrame(res.data)


def etudiants_sans_note(client) -> pd.DataFrame:
    res = client.table("v_etudiants_sans_note").select("*").execute()
    return pd.DataFrame(res.data)


def classement_etudiants(client, classe: str | None = None) -> pd.DataFrame:
    q = client.table("v_classement_etudiants").select("*")
    if classe:
        q = q.eq("classe_texte", classe)
    res = q.order("rang").execute()
    return pd.DataFrame(res.data)


def recherche_notes(
    client,
    matricule: str = "", nom: str = "", prenoms: str = "",
    classe: str = "", ue: str = "", campus: str = "",
    limite: int = 1000,
) -> pd.DataFrame:
    q = client.table("notes_centrales").select("*")
    if matricule:
        q = q.ilike("matricule", f"%{matricule}%")
    if nom:
        q = q.ilike("nom", f"%{nom}%")
    if prenoms:
        q = q.ilike("prenoms", f"%{prenoms}%")
    if classe:
        q = q.ilike("classe_texte", f"%{classe}%")
    if ue:
        q = q.ilike("ue", f"%{ue}%")
    if campus:
        q = q.ilike("campus_texte", f"%{campus}%")
    res = q.limit(limite).execute()
    return pd.DataFrame(res.data)
