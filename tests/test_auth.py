import pytest
from werkzeug.security import generate_password_hash


def test_register_success(client, session):
    """
    Test successful user registration.
    Expects:
        - Status code 201 (Created)
        - Confirmation message in the response
    """
    payload = {"email": "test@example.fr", "password": "supersecret"}
    resp = client.post("/api/auth/register", json=payload)
    assert resp.status_code == 201
    assert resp.json["message"] == "Subscription done !"


def test_register_missing_fields(client, session):
    """
    Test registration with missing required fields.
    Expects:
        - Status code 400 (Bad Request)
        - Error message indicating missing fields
    """
    payload = {"email": "test2@example.com"}
    resp = client.post("/api/auth/register", json=payload)
    assert resp.status_code == 400
    assert "Missing fields" in resp.json["error"]


def test_register_existing_email(client, session):
    """
    Test registration with an already existing email.
    Expects:
        - Status code 409 (Conflict)
        - Error message indicating the user already exists
    """
    payload = {"email": "duplicate@example.fr", "password": "pwd"}
    client.post("/api/auth/register", json=payload)
    resp2 = client.post("/api/auth/register", json=payload)
    assert resp2.status_code == 409
    assert f"User {payload['email']} already exist." in resp2.json["error"]


def test_register_unexpected_error(monkeypatch, client, session):
    """
    Test registration when an unexpected database error occurs.
    Expects:
        - Status code 500 (Internal Server Error)
        - Error message indicating an internal error
    """
    payload = {"email": "boom@example.fr", "password": "pwd"}

    def raise_exc(*args, **kwargs):
        raise Exception("Simulated DB Failure")

    monkeypatch.setattr(session, "commit", raise_exc)

    resp = client.post("/api/auth/register", json=payload)
    assert resp.status_code == 500
    assert "Internal error" in resp.json["error"]


@pytest.fixture
def user_in_db(session):
    """
    Fixture: Create a user in the database for authentication tests.
    Returns:
        User instance
    """
    from api_ecommerce.models import User

    user = User(
        email="loginuser@example.com",
        password=generate_password_hash("strongpass", method="pbkdf2:sha256"),
        role="user",
    )
    session.add(user)
    session.commit()
    return user


def test_login_success(client, session, user_in_db):
    """
    Test successful user login.
    Expects:
        - Status code 200 (OK)
        - JWT token present in the response
    """
    payload = {"email": "loginuser@example.com", "password": "strongpass"}
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == 200
    json = response.get_json()
    assert "token" in json and len(json["token"]) > 10  # JWT is returned


def test_login_missing_fields(client):
    """
    Test login with missing required fields.
    Expects:
        - Status code 400 (Bad Request)
        - Error message indicating missing fields
    """
    payload = {"email": "user@example.com"}  # password missing
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == 400
    assert "Missing fields" in response.get_json().get("error", "")


def test_login_user_not_exist(client):
    """
    Test login attempt with a non-existent user.
    Expects:
        - Status code 409 (Conflict)
        - Error message indicating user does not exist
    """
    payload = {"email": "ghost@example.com", "password": "anything"}
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == 409  # Used instead of 404, as per implementation
    assert "not exist" in response.get_json().get("error", "")


def test_login_bad_password(client, session, user_in_db):
    """
    Test login with a wrong password.
    Expects:
        - Status code 401 (Unauthorized)
        - Error message indicating verification failure
    """
    payload = {"email": "loginuser@example.com", "password": "badpassword"}
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == 401
    assert "Could not verify" in response.get_json().get("error", "")
