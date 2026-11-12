from typing import Any, Dict, List, Optional

from langchain_core.tools import tool

# Données de référence pour les outils de l'agent
REFERENTIEL_BATIMENTS = {
    "bat-a": {
        "id": "bat-a",
        "nom": "Bâtiment A - Sciences et Technologies",
        "zone": "Nord",
        "surface": 4500.0,
        "consommation_moyenne_kwh": 3120.5,
        "eco_score": 78
    },
    "bat-b": {
        "id": "bat-b",
        "nom": "Bâtiment B - Enseignement et Amphis",
        "zone": "Est",
        "surface": 6200.0,
        "consommation_moyenne_kwh": 5410.2,
        "eco_score": 64
    },
    "bat-c": {
        "id": "bat-c",
        "nom": "Bâtiment C - Laboratoires de Recherche",
        "zone": "Ouest",
        "surface": 3800.0,
        "consommation_moyenne_kwh": 4890.0,
        "eco_score": 58
    },
    "bat-d": {
        "id": "bat-d",
        "nom": "Bâtiment D - Administration & Vie Étudiante",
        "zone": "Sud",
        "surface": 2900.0,
        "consommation_moyenne_kwh": 1850.3,
        "eco_score": 85
    }
}


@tool
def classement_batiments(module: str = "energie", debut: Optional[str] = None, fin: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Classe les bâtiments du campus par consommation totale pour un module donné (ex: 'energie', 'eau') entre deux dates.
    Renvoie la liste triée de la plus forte à la plus faible consommation.
    """
    batiments_data = list(REFERENTIEL_BATIMENTS.values())
    sorted_bat = sorted(batiments_data, key=lambda b: b["consommation_moyenne_kwh"], reverse=True)
    return [
        {
            "rang": idx + 1,
            "batiment_id": b["id"],
            "nom": b["nom"],
            "consommation_kwh": b["consommation_moyenne_kwh"],
            "eco_score": b["eco_score"],
            "module": module
        }
        for idx, b in enumerate(sorted_bat)
    ]


@tool
def consommation(module: str, batiment_id: str, debut: Optional[str] = None, fin: Optional[str] = None) -> Dict[str, Any]:
    """
    Renvoie la série et la synthèse de consommation d'un module ('energie', 'eau') pour un bâtiment spécifique.
    """
    bat = REFERENTIEL_BATIMENTS.get(batiment_id)
    if not bat:
        return {"erreur": f"Bâtiment '{batiment_id}' introuvable dans le référentiel"}

    return {
        "batiment_id": bat["id"],
        "nom": bat["nom"],
        "module": module,
        "consommation_totale": bat["consommation_moyenne_kwh"],
        "unite": "kWh" if module == "energie" else "m3",
        "moyenne_journaliere": round(bat["consommation_moyenne_kwh"] / 30, 2),
        "heures_pleines_pct": 68.5,
        "heures_creuses_pct": 31.5
    }


@tool
def alertes(statut: Optional[str] = "ouverte", batiment_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Renvoie la liste des alertes de capteurs filtrées par statut ('ouverte', 'acquittee', 'resolue') et bâtiment.
    """
    mock_alertes = [
        {
            "id": 1,
            "batiment_id": "bat-b",
            "capteur_id": "sensor-elec-batB-amphi",
            "type": "energie",
            "gravite": "critique",
            "statut": "ouverte",
            "message": "Dépassement du seuil de puissance : 84.5 kW (> 80 kW)",
            "ouverte_le": "2026-11-12T08:30:00Z"
        },
        {
            "id": 2,
            "batiment_id": "bat-a",
            "capteur_id": "sensor-eau-batA-01",
            "type": "eau",
            "gravite": "critique",
            "statut": "ouverte",
            "message": "Débit d'eau continu anormal la nuit (suspicion de fuite)",
            "ouverte_le": "2026-11-12T03:15:00Z"
        }
    ]

    filtered = mock_alertes
    if statut:
        filtered = [a for a in filtered if a["statut"] == statut]
    if batiment_id:
        filtered = [a for a in filtered if a["batiment_id"] == batiment_id]
    return filtered


@tool
def details_referentiel(type_entite: str, identifiant: str) -> Dict[str, Any]:
    """
    Renvoie la fiche descriptive détaillée d'un bâtiment ou d'un capteur du campus.
    type_entite : 'batiment' ou 'capteur'.
    """
    if type_entite == "batiment":
        bat = REFERENTIEL_BATIMENTS.get(identifiant)
        if bat:
            return bat
        return {"erreur": f"Bâtiment '{identifiant}' non trouvé"}
    elif type_entite == "capteur":
        return {
            "id": identifiant,
            "etat": "actif",
            "type": "energie",
            "frequence_mesure": "10s",
            "derniere_mesure": 42.1,
            "unite": "kWh"
        }
    return {"erreur": f"Type d'entité '{type_entite}' non supporté"}


ALL_TOOLS = [classement_batiments, consommation, alertes, details_referentiel]


def get_tools_for_role(role: str) -> List[Any]:
    """
    Filtre les outils disponibles selon le rôle de l'utilisateur (RNF4 / T09 / Section 2.3).
    Gestionnaire et Direction ont accès à l'ensemble des outils d'analyse.
    Les étudiants ou techniciens ont accès à un sous-ensemble approprié.
    """
    if role in ["gestionnaire", "direction"]:
        return ALL_TOOLS
    elif role == "technicien":
        return [alertes, details_referentiel]
    else:  # etudiant
        return [classement_batiments]
