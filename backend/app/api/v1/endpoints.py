from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from app.agent.assistant import ask_assistant
from app.auth.deps import UserPayload, get_current_user, require_roles
from app.logger import logger

router = APIRouter()


# -------------------------------------------------------------
# Modèles Pydantic pour le contrat OpenAPI (T01 / T06)
# -------------------------------------------------------------

class BatimentResponse(BaseModel):
    id: str
    nom: str
    zone: str
    surface: float
    coordonnees: Dict[str, float]


class SalleResponse(BaseModel):
    id: str
    batiment_id: str
    nom: str
    capacite: int
    usage: str
    etage: int


class CapteurResponse(BaseModel):
    id: str
    salle_id: str
    type: str
    unite: str
    etat: str
    derniere_mesure: Optional[float] = None


class SeriePoint(BaseModel):
    horodatage: str
    valeur: float


class ConsommationResponse(BaseModel):
    batiment_id: str
    module: str
    unite: str
    total_periode: float
    points: List[SeriePoint]


class AlerteItem(BaseModel):
    id: int
    capteur_id: str
    batiment_id: str
    type: str
    gravite: str
    statut: str
    message: str
    ouverte_le: str


class AssistantQuestionRequest(BaseModel):
    question: str = Field(..., json_schema_extra={"example": "Quel bâtiment a le plus consommé la semaine dernière ?"})


class AssistantResponse(BaseModel):
    question: str
    reponse: str
    outils_appeles: List[Dict[str, Any]]
    duree_ms: int
    modele: str


# -------------------------------------------------------------
# Données factices structurées conformes à OpenAPI (T01 / T06)
# -------------------------------------------------------------

MOCK_BATIMENTS = [
    {
        "id": "bat-a",
        "nom": "Bâtiment A - Sciences et Technologies",
        "zone": "Nord",
        "surface": 4500.0,
        "coordonnees": {"lat": 48.8580, "lng": 2.3510}
    },
    {
        "id": "bat-b",
        "nom": "Bâtiment B - Enseignement et Amphis",
        "zone": "Est",
        "surface": 6200.0,
        "coordonnees": {"lat": 48.8560, "lng": 2.3540}
    },
    {
        "id": "bat-c",
        "nom": "Bâtiment C - Laboratoires de Recherche",
        "zone": "Ouest",
        "surface": 3800.0,
        "coordonnees": {"lat": 48.8590, "lng": 2.3480}
    },
    {
        "id": "bat-d",
        "nom": "Bâtiment D - Administration & Vie Étudiante",
        "zone": "Sud",
        "surface": 2900.0,
        "coordonnees": {"lat": 48.8540, "lng": 2.3500}
    }
]

MOCK_CAPTEURS = [
    {"id": "sensor-elec-batA-01", "salle_id": "salle-a-101", "type": "energie", "unite": "kWh", "etat": "actif", "derniere_mesure": 42.5},
    {"id": "sensor-elec-batB-amphi", "salle_id": "salle-b-amphi", "type": "energie", "unite": "kWh", "etat": "actif", "derniere_mesure": 84.1},
    {"id": "sensor-eau-batA-01", "salle_id": "salle-a-101", "type": "eau", "unite": "m3", "etat": "actif", "derniere_mesure": 3.8},
    {"id": "sensor-co2-batB-amphi", "salle_id": "salle-b-amphi", "type": "co2", "unite": "ppm", "etat": "actif", "derniere_mesure": 650.0},
    {"id": "sensor-dechets-batA-01", "salle_id": "salle-a-101", "type": "dechets", "unite": "%", "etat": "actif", "derniere_mesure": 72.0},
]


# -------------------------------------------------------------
# Endpoints
# -------------------------------------------------------------

@router.get("/health", summary="Vérification de l'état de l'API")
async def health_check():
    """Point de contrôle de santé du système (CI & monitoring)."""
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "ecosmart-backend",
        "sprint": 1
    }


@router.get("/referentiel/batiments", response_model=List[BatimentResponse], summary="Référentiel des bâtiments")
async def get_batiments(current_user: UserPayload = Depends(get_current_user)):
    """Renvoie la liste des bâtiments du campus (RF02)."""
    return MOCK_BATIMENTS


@router.get("/referentiel/capteurs", response_model=List[CapteurResponse], summary="Référentiel des capteurs")
async def get_capteurs(
    type_capteur: Optional[str] = Query(None, description="Filtrer par type : energie, eau, dechets, co2..."),
    current_user: UserPayload = Depends(get_current_user)
):
    """Renvoie les capteurs enregistrés (RF02)."""
    if type_capteur:
        return [c for c in MOCK_CAPTEURS if c["type"] == type_capteur]
    return MOCK_CAPTEURS


@router.get("/series/consommation", response_model=ConsommationResponse, summary="Séries agrégées de consommation")
async def get_series_consommation(
    batiment_id: str = Query("bat-a", description="Identifiant du bâtiment"),
    module: str = Query("energie", description="Module concerné"),
    current_user: UserPayload = Depends(get_current_user)
):
    """Renvoie l'historique et les agrégats de consommation d'un bâtiment (RF09 / T11)."""
    # Génération d'une série factice représentative pour le frontend
    now = datetime.now(timezone.utc)
    points = [
        SeriePoint(
            horodatage=now.replace(hour=h, minute=0, second=0).isoformat(),
            valeur=round(15.0 + (35.0 if 8 <= h <= 18 else 8.0) + (h % 3) * 1.5, 2)
        )
        for h in range(24)
    ]
    total = sum(p.valeur for p in points)
    return ConsommationResponse(
        batiment_id=batiment_id,
        module=module,
        unite="kWh" if module == "energie" else "m3",
        total_periode=round(total, 2),
        points=points
    )


@router.get("/alertes", response_model=List[AlerteItem], summary="Liste des alertes")
async def get_alertes(
    statut: Optional[str] = Query("ouverte", description="Statut : ouverte, acquittee, resolue"),
    current_user: UserPayload = Depends(get_current_user)
):
    """Liste les alertes détectées sur le campus (RF06 / T18)."""
    return [
        AlerteItem(
            id=1,
            capteur_id="sensor-elec-batB-amphi",
            batiment_id="bat-b",
            type="energie",
            gravite="critique",
            statut="ouverte",
            message="Pic de consommation amphi Turing : 84.1 kW (> 80.0 kW)",
            ouverte_le="2026-11-12T08:30:00Z"
        ),
        AlerteItem(
            id=2,
            capteur_id="sensor-eau-batA-01",
            batiment_id="bat-a",
            type="eau",
            gravite="critique",
            statut="ouverte",
            message="Débit continu anormal en période nocturne (suspicion fuite)",
            ouverte_le="2026-11-12T03:15:00Z"
        )
    ]


@router.post(
    "/assistant",
    response_model=AssistantResponse,
    summary="Interrogation de l'assistant EcoSmart en langage naturel (T09, RF24, RF25)",
    dependencies=[Depends(require_roles(["gestionnaire", "direction", "technicien", "etudiant"]))]
)
async def post_assistant_question(
    request: AssistantQuestionRequest,
    current_user: UserPayload = Depends(get_current_user)
):
    """
    Point d'accès de l'assistant LangChain.
    Exécute les outils en fonction du rôle de l'utilisateur, journalise l'échange
    et renvoie la réponse rédigée ainsi que les sources des chiffres (RF24, RF25).
    """
    logger.info(
        f"Requête assistant de l'utilisateur {current_user.email} (rôle: {current_user.role})",
        extra={"extra_data": {"user": current_user.email, "role": current_user.role}}
    )
    result = ask_assistant(question=request.question, role=current_user.role)
    return AssistantResponse(**result)
