import pytest
from httpx import ASGITransport, AsyncClient

from app.agent.assistant import EcoSmartAssistant, ask_assistant
from app.agent.tools import (
    ALL_TOOLS,
    alertes,
    classement_batiments,
    consommation,
    details_referentiel,
    get_tools_for_role,
)
from app.auth.security import create_access_token
from app.main import app


def test_tools_direct_execution():
    # 1. Test classement_batiments (T09 un outil principal)
    classement = classement_batiments.invoke({"module": "energie"})
    assert isinstance(classement, list)
    assert len(classement) >= 4
    # Doit être trié par consommation décroissante
    assert classement[0]["consommation_kwh"] >= classement[1]["consommation_kwh"]

    # 2. Test consommation
    conso = consommation.invoke({"module": "energie", "batiment_id": "bat-a"})
    assert conso["batiment_id"] == "bat-a"
    assert "consommation_totale" in conso
    assert conso["unite"] == "kWh"

    # 3. Test alertes
    alt = alertes.invoke({"statut": "ouverte"})
    assert isinstance(alt, list)

    # 4. Test details_referentiel
    details = details_referentiel.invoke({"type_entite": "batiment", "identifiant": "bat-a"})
    assert details["id"] == "bat-a"
    assert "surface" in details


def test_tools_filtering_by_role():
    # Gestionnaire a tous les outils
    tools_gestionnaire = get_tools_for_role("gestionnaire")
    assert len(tools_gestionnaire) == len(ALL_TOOLS)

    # Étudiant a uniquement les outils de consultation / classement
    tools_etudiant = get_tools_for_role("etudiant")
    assert len(tools_etudiant) == 1
    assert tools_etudiant[0].name == "classement_batiments"


def test_assistant_invoke_question_classement():
    assistant = EcoSmartAssistant(role="gestionnaire")
    res = assistant.invoke("Quel bâtiment a le plus consommé la semaine dernière ?")
    assert "reponse" in res
    assert "outils_appeles" in res
    assert len(res["outils_appeles"]) >= 1
    assert res["outils_appeles"][0]["outil"] == "classement_batiments"
    # Vérification que le nom et les kWh sont cités
    assert "kWh" in res["reponse"]
    assert "Bâtiment" in res["reponse"]


def test_ask_assistant_wrapper():
    res = ask_assistant("Quelles sont les alertes en cours ?", role="gestionnaire")
    assert "reponse" in res
    assert len(res["outils_appeles"]) >= 1
    assert res["outils_appeles"][0]["outil"] == "alertes"


@pytest.mark.asyncio
async def test_assistant_endpoint_with_jwt():
    token = create_access_token({"sub": "admin@campus.fr", "role": "gestionnaire"})
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/assistant",
            headers={"Authorization": f"Bearer {token}"},
            json={"question": "Quel bâtiment a le plus consommé ?"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "reponse" in data
        assert "outils_appeles" in data
        assert len(data["outils_appeles"]) >= 1
        assert "modele" in data
        assert "duree_ms" in data
