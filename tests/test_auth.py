def test_register_user(client):
    response = client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["email"] == "test@example.com"
    assert "id" in data
    assert "created_at" in data
    assert "password" not in data
    assert "hashed_password" not in data


def test_register_duplicate_email(client):
    user_data = {
        "email": "test@example.com",
        "password": "password123",
    }

    first_response = client.post(
        "/auth/register",
        json=user_data,
    )

    second_response = client.post(
        "/auth/register",
        json=user_data,
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 400

    assert second_response.json()["detail"] == (
        "Email already registered"
    )


def test_login_user(client):
    client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "password": "password123",
        },
    )

    response = client.post(
        "/auth/login",
        data={
            "username": "test@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_with_wrong_password(client):
    client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "password": "password123",
        },
    )

    response = client.post(
        "/auth/login",
        data={
            "username": "test@example.com",
            "password": "wrongpassword",
        },
    )

    assert response.status_code == 401

    assert response.json()["detail"] == (
        "Invalid email or password"
    )


def test_read_current_user(client):
    client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "password": "password123",
        },
    )

    login_response = client.post(
        "/auth/login",
        data={
            "username": "test@example.com",
            "password": "password123",
        },
    )

    token = login_response.json()["access_token"]

    response = client.get(
        "/users/me",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["email"] == "test@example.com"