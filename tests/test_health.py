def test_root(client):
    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == (
        "Welcome to Fraud Detection API"
    )

    assert data["docs"] == "/docs"


def test_health_check(client):
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert data["message"] == (
        "Fraud Detection API is running"
    )