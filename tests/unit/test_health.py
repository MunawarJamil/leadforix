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
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == service_name
