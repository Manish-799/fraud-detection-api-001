def register_and_login(
    client,
    email,
    password="password123",
):
    client.post(
        "/auth/register",
        json={
            "email": email,
            "password": password,
        },
    )

    login_response = client.post(
        "/auth/login",
        data={
            "username": email,
            "password": password,
        },
    )

    return login_response.json()["access_token"]


def get_auth_headers(token):
    return {
        "Authorization": f"Bearer {token}",
    }


def get_test_transaction():
    return {
        "type": "TRANSFER",
        "amount": 181,
        "oldbalanceOrg": 181,
        "newbalanceOrig": 0,
        "oldbalanceDest": 0,
        "newbalanceDest": 0,
    }


def test_predict_requires_authentication(client):
    response = client.post(
        "/predict",
        json=get_test_transaction(),
    )

    assert response.status_code == 401


def test_create_prediction(client):
    token = register_and_login(
        client,
        email="test@example.com",
    )

    response = client.post(
        "/predict",
        json=get_test_transaction(),
        headers=get_auth_headers(token),
    )

    assert response.status_code == 200

    data = response.json()

    assert "prediction_id" in data
    assert data["prediction"] in {
        "fraud",
        "not_fraud",
    }

    assert data["risk_level"] in {
        "very_low",
        "low",
        "medium",
        "high",
    }

    assert 0 <= data["fraud_probability"] <= 1
    assert data["threshold_used"] == 0.8
    assert data["model_version"] == "v1.0"


def test_prediction_history(client):
    token = register_and_login(
        client,
        email="test@example.com",
    )

    headers = get_auth_headers(token)

    client.post(
        "/predict",
        json=get_test_transaction(),
        headers=headers,
    )

    response = client.get(
        "/predictions",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1

    assert data[0]["transaction_type"] == "TRANSFER"

    assert data[0]["amount"] == 181


def test_user_cannot_read_another_users_prediction(
    client,
):
    first_user_token = register_and_login(
        client,
        email="first@example.com",
    )

    prediction_response = client.post(
        "/predict",
        json=get_test_transaction(),
        headers=get_auth_headers(first_user_token),
    )

    prediction_id = prediction_response.json()[
        "prediction_id"
    ]

    second_user_token = register_and_login(
        client,
        email="second@example.com",
    )

    response = client.get(
        f"/predictions/{prediction_id}",
        headers=get_auth_headers(second_user_token),
    )

    assert response.status_code == 404

    assert response.json()["detail"] == (
        "Prediction not found"
    )