"""
Détection des erreurs sur les lignes extraites des fichiers Excel avant import.
Types d'erreurs gérés : ligne_vide, matricule_absent, doublon, feuille_vide,
fichier_vide, colonnes_manquantes.
"""
from dataclasses import dataclass, field

COLONNES_REQUISES = [
    "MATRICULE", "NOM", "PRENOMS", "CLASSE", "UE", "CAMPUS", "NOTE1", "NOTE2", "MOYENNE"
]


@dataclass
class ErreurLigne:
    nom_fichier: str
    feuille: str
    ligne_excel: int
    type_erreur: str
    detail: str


@dataclass
class RapportValidation:
    erreurs: list[ErreurLigne] = field(default_factory=list)

    def ajouter(self, nom_fichier, feuille, ligne_excel, type_erreur, detail):
        self.erreurs.append(ErreurLigne(nom_fichier, feuille, ligne_excel, type_erreur, detail))

    @property
    def nb_erreurs(self):
        return len(self.erreurs)

    def par_type(self):
        compte = {}
        for e in self.erreurs:
            compte[e.type_erreur] = compte.get(e.type_erreur, 0) + 1
        return compte


def verifier_colonnes(colonnes_presentes: list[str]) -> list[str]:
    """Retourne la liste des colonnes requises manquantes (comparaison insensible à la casse)."""
    presentes_norm = {c.strip().upper() for c in colonnes_presentes if c}
    return [c for c in COLONNES_REQUISES if c not in presentes_norm]


def ligne_est_vide(ligne: dict) -> bool:
    """Une ligne est considérée vide si NOM, PRENOMS et MATRICULE sont tous absents."""
    nom = str(ligne.get("NOM") or "").strip()
    prenoms = str(ligne.get("PRENOMS") or "").strip()
    matricule = str(ligne.get("MATRICULE") or "").strip()
    return not nom and not prenoms and not matricule


def matricule_absent(ligne: dict) -> bool:
    return not str(ligne.get("MATRICULE") or "").strip()
