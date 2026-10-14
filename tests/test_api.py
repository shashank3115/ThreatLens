from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    assert client.get("/api/health").json()["status"] == "ok"


def test_sample_events_are_available_for_the_event_inspector():
    response = client.get("/api/sample-events")
    assert response.status_code == 200
    assert response.json()[0]["event_id"] == "evt-001"


def test_evaluation_reports_calculated_synthetic_metrics():
    response = client.get("/api/evaluation")
    assert response.status_code == 200
    data = response.json()
    assert data["dataset_size"] == 6
    assert data["metrics"][0]["precision"] == 0.5
    assert data["metrics"][0]["recall"] == 1.0
    assert data["metrics"][0]["false_positive_rate"] == 0.2


def test_analysis_and_empty_input():
    response = client.post("/api/analyze", json={"report": "rundll32.exe and powershell -enc."})
    assert response.status_code == 200
    assert response.json()["summary"]["evidence_supported"] == 2
    assert client.post("/api/analyze", json={"report": "   "}).status_code == 422
    assert client.post("/api/analyze", json={"report": 42}).status_code == 422


def test_unsupported_candidates_remain_explicitly_unsupported():
    response = client.post("/api/analyze", json={"report": "A report without either baseline literal."})
    assert response.status_code == 200
    for rule in response.json()["rules"]:
        assert rule["structural_valid"] is True
        assert rule["evidence_supported"] is False
        assert rule["unsupported_reason"]


def test_malformed_json_is_rejected():
    assert client.post("/api/analyze", content="not json", headers={"content-type":"application/json"}).status_code == 422
