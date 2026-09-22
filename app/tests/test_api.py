from fastapi.testclient import TestClient

from app.api import app, received_metrics

client = TestClient(app)


def setup_function():
    received_metrics.clear()


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_receive_metrics():
    payload = {
        "agent": "system-metrics-agent",
        "event_type": "system_metrics",
        "data": {
            "timestamp": "2026-08-27T12:00:00+00:00",
            "hostname": "server-01",
            "cpu": {"percent": 20.0},
            "memory": {"percent": 40.0},
            "system": {"load_1m": 0.1},
        },
    }

    response = client.post("/metrics", json=payload)

    assert response.status_code == 201
    assert response.json()["status"] == "received"


def test_latest_metrics_when_empty():
    response = client.get("/metrics/latest")

    assert response.status_code == 404
