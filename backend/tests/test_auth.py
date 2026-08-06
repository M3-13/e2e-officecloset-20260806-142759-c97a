from datetime import UTC, datetime, timedelta

import pytest
from jose import jwt

from auth import JWT_ALGORITHM, create_access_token
from database import SessionLocal
from models import User

TEST_JWT_SECRET = "test-secret-key-for-auth-tests"


@pytest.fixture(autouse=True)
def set_jwt_secret(monkeypatch):
    monkeypatch.setenv("JWT_SECRET", TEST_JWT_SECRET)


@pytest.fixture(autouse=True)
def clean_users():
    yield
    db = SessionLocal()
    try:
        db.query(User).delete()
        db.commit()
    finally:
        db.close()


def test_register_success(client):
    response = client.post(
        "/api/auth/register",
        json={"email": "newuser@example.com", "password": "securepass123"},
    )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    payload = jwt.decode(data["access_token"], TEST_JWT_SECRET, algorithms=[JWT_ALGORITHM])
    assert "user_id" in payload
    assert "exp" in payload
    assert "email" not in payload


def test_register_duplicate(client):
    client.post(
        "/api/auth/register",
        json={"email": "dup@example.com", "password": "pass1"},
    )
    response = client.post(
        "/api/auth/register",
        json={"email": "dup@example.com", "password": "pass2"},
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "Ungültige Anmeldedaten"


def test_register_invalid_email(client):
    response = client.post(
        "/api/auth/register",
        json={"email": "not-an-email", "password": "password123"},
    )
    assert response.status_code == 422


def test_login_success(client):
    client.post(
        "/api/auth/register",
        json={"email": "login_test@example.com", "password": "mypassword"},
    )
    response = client.post(
        "/api/auth/login",
        json={"email": "login_test@example.com", "password": "mypassword"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    payload = jwt.decode(data["access_token"], TEST_JWT_SECRET, algorithms=[JWT_ALGORITHM])
    assert "user_id" in payload


def test_login_wrong_password(client):
    client.post(
        "/api/auth/register",
        json={"email": "wrongpw@example.com", "password": "correct"},
    )
    response = client.post(
        "/api/auth/login",
        json={"email": "wrongpw@example.com", "password": "wrong"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Ungültige Anmeldedaten"


def test_login_nonexistent_user(client):
    response = client.post(
        "/api/auth/login",
        json={"email": "ghost@example.com", "password": "nope"},
    )
    assert response.status_code == 401


def test_protected_route_without_token(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 401


def test_protected_route_with_valid_token(client):
    reg = client.post(
        "/api/auth/register",
        json={"email": "authed@example.com", "password": "pass"},
    )
    token = reg.json()["access_token"]
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert "user_id" in response.json()


def test_protected_route_expired_token(client):
    expire = datetime.now(UTC) - timedelta(hours=1)
    payload = {"user_id": 1, "exp": expire}
    expired_token = jwt.encode(payload, TEST_JWT_SECRET, algorithm=JWT_ALGORITHM)
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    assert response.status_code == 401


def test_protected_route_unknown_user(client):
    token = create_access_token(user_id=99999)
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403


def test_error_messages_no_email_leak(client):
    client.post(
        "/api/auth/register",
        json={"email": "leak@example.com", "password": "p"},
    )
    dup = client.post(
        "/api/auth/register",
        json={"email": "leak@example.com", "password": "q"},
    )
    assert "leak@example.com" not in dup.text

    login_resp = client.post(
        "/api/auth/login",
        json={"email": "leak@example.com", "password": "wrong"},
    )
    assert "leak@example.com" not in login_resp.text


def test_password_is_hashed_in_db(client):
    client.post(
        "/api/auth/register",
        json={"email": "hashed@example.com", "password": "plaintext"},
    )
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "hashed@example.com").first()
        assert user is not None
        assert user.hashed_password != "plaintext"
        assert user.hashed_password.startswith("$2b$")
    finally:
        db.close()
