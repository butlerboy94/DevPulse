# Tests for POST /auth/register and POST /auth/login (registration,
# duplicate-email/username rejection, login success/failure).
def test_register_new_user(client):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "new@example.com", "username": "newuser", "password": "password123"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "new@example.com"
    assert data["username"] == "newuser"
    assert "hashed_password" not in data


def test_register_duplicate_email_is_rejected(client):
    payload = {"email": "dup@example.com", "username": "userone", "password": "password123"}
    client.post("/api/v1/auth/register", json=payload)

    payload["username"] = "usertwo"
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 400


def test_login_with_correct_credentials(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "login@example.com", "username": "loginuser", "password": "password123"},
    )
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "login@example.com", "password": "password123"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_login_with_wrong_password_is_rejected(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "wrongpw@example.com", "username": "wrongpwuser", "password": "password123"},
    )
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "wrongpw@example.com", "password": "not-the-password"},
    )
    assert response.status_code == 401
