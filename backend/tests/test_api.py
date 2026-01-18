from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_create_and_get_loan_detail():
    payload = {"amount": 250000, "apr": 5.5, "term_months": 360}

    r = client.post("/loans", json=payload)
    assert r.status_code == 200
    created = r.json()

    assert "id" in created
    assert created["amount"] == 250000
    assert created["apr"] == 5.5
    assert created["term_months"] == 360
    assert created["monthly_payment"] == 1419.47 

    loan_id = created["id"]

    r2 = client.get(f"/loans/{loan_id}")
    assert r2.status_code == 200
    detail = r2.json()

    assert detail["id"] == loan_id
    assert detail["monthly_payment"] == 1419.47
    assert "schedule_preview" in detail
    assert len(detail["schedule_preview"]) == 12
