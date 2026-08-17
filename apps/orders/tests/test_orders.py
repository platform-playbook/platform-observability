from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "UP"}


def test_create_order():
    response = client.post(
        "/orders",
        json={
            "product_id": "P100",
            "quantity": 2,
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["product_id"] == "P100"
    assert body["quantity"] == 2
    assert body["status"] == "created"
    assert "order_id" in body
