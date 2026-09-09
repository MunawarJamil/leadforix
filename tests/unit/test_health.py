from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from apps.services.agent_service.app.main import app as agent_app
from apps.services.auth_service.app.main import app as auth_app
from apps.services.campaign_service.app.main import app as campaign_app
from apps.services.knowledge_service.app.main import app as knowledge_app
from apps.services.lead_service.app.main import app as lead_app
from apps.services.outreach_service.app.main import app as outreach_app
from apps.services.research_service.app.main import app as research_app
from apps.services.workspace_service.app.main import app as workspace_app

SERVICES = [
    ("agent_service", agent_app),
    ("auth_service", auth_app),
    ("campaign_service", campaign_app),
    ("knowledge_service", knowledge_app),
    ("lead_service", lead_app),
    ("outreach_service", outreach_app),
    ("research_service", research_app),
    ("workspace_service", workspace_app),
]


@pytest.mark.parametrize("service_name,app", SERVICES)
def test_service_health(service_name: str, app):
    """
    Verify that all 8 microservices expose a responsive /health endpoint.
    Mocks live database probe to allow offline unit tests to pass deterministically.
    """
    with patch("apps.services.auth_service.app.main.ping_database", return_value=True):
        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == service_name


def test_auth_service_liveness_probe():
    """
    Verify /health/live returns 200 without querying database.
    """
    client = TestClient(auth_app)
    response = client.get("/health/live")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "live"
    assert data["service"] == "auth_service"


def test_auth_service_readiness_probe_healthy():
    """
    Verify /health/ready returns 200 when database is reachable.
    """
    with patch("apps.services.auth_service.app.main.ping_database", return_value=True):
        client = TestClient(auth_app)
        response = client.get("/health/ready")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"
        assert data["database"] == "connected"


def test_auth_service_readiness_probe_degraded():
    """
    Verify /health/ready returns 503 when database is unreachable.
    """
    with patch("apps.services.auth_service.app.main.ping_database", return_value=False):
        client = TestClient(auth_app)
        response = client.get("/health/ready")
        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "degraded"
        assert data["database"] == "disconnected"
