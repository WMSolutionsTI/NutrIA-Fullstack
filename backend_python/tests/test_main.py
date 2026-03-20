from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/api/v1/monitor/health")
    assert response.status_code == 200
    assert response.json().get("status") == "ok"


def test_workflow_logs():
    response = client.get("/api/v1/workflows/logs/123")
    assert response.status_code == 200
    data = response.json()
    assert data["workflow_id"] == "123"
    assert "logs" in data
