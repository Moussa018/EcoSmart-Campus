import pytest
from httpx import ASGITransport, AsyncClient

from app.auth.security import create_access_token
from app.main import app


@pytest.fixture
def auth_headers():
    token = create_access_token({"sub": "admin@campus.fr", "role": "gestionnaire"})
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_health_check():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["sprint"] == 1


@pytest.mark.asyncio
async def test_openapi_contract_available():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "paths" in data
        assert "/api/v1/auth/login" in data["paths"]
        assert "/api/v1/referentiel/batiments" in data["paths"]
        assert "/api/v1/assistant" in data["paths"]


@pytest.mark.asyncio
async def test_referentiel_batiments(auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/referentiel/batiments", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 4
        assert any(b["id"] == "bat-a" for b in data)


@pytest.mark.asyncio
async def test_series_consommation(auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/series/consommation?batiment_id=bat-a&module=energie", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["batiment_id"] == "bat-a"
        assert data["module"] == "energie"
        assert len(data["points"]) == 24
