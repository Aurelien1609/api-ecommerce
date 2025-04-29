import pytest
from api_ecommerce.models import Command, CommandLign, User, Product
from werkzeug.security import generate_password_hash
import datetime


@pytest.fixture
def user(session):
    """
    Fixture: Create a regular user for authentication.
    """
    user = User(
        email="user1@example.com",
        password=generate_password_hash("userpass", method="pbkdf2:sha256"),
        role="user",
    )
    session.add(user)
    session.commit()
    return user


@pytest.fixture
def admin(session):
    """
    Fixture: Create an admin user for authentication.
    """
    admin = User(
        email="admin@example.com",
        password=generate_password_hash("adminpass", method="pbkdf2:sha256"),
        role="admin",
    )
    session.add(admin)
    session.commit()
    return admin


@pytest.fixture
def user_token(client, user):
    """
    Fixture: Log the user in and return a valid JWT token.
    """
    response = client.post(
        "/api/auth/login", json={"email": user.email, "password": "userpass"}
    )
    return response.json["token"]


@pytest.fixture
def admin_token(client, admin):
    """
    Fixture: Log the admin in and return a valid JWT token.
    """
    response = client.post(
        "/api/auth/login", json={"email": admin.email, "password": "adminpass"}
    )
    return response.json["token"]


@pytest.fixture
def product(session):
    """
    Fixture: Create a product for use in command tests.
    """
    p = Product(
        name="Chips",
        description="Yummy",
        category="Snack",
        price=1.5,
        stock=10,
        date_creation=datetime.datetime.now(),
    )
    session.add(p)
    session.commit()
    return p


@pytest.fixture
def command(session, user):
    """
    Fixture: Create a command for the given user.
    """
    c = Command(
        user_id=user.id,
        status="on hold",
        address_delivery="Street 1",
        date_command=datetime.datetime.now(),
    )
    session.add(c)
    session.commit()
    return c


@pytest.fixture
def command_lign(session, command, product):
    """
    Fixture: Create a command line for a command.
    """
    cl = CommandLign(
        command_id=command.id, product_id=product.id, quantity=2, price=product.price
    )
    session.add(cl)
    session.commit()
    return cl


def test_list_commands_user(client, session, user_token, user, command):
    """
    Test list_commands returns only the commands of the current user if user is not admin.
    """
    headers = {"Authorization": f"Bearer {user_token}"}
    response = client.get("/api/commands", headers=headers)
    assert response.status_code == 200
    commands = response.get_json()
    assert any(cmd["command_id"] == command.id for cmd in commands)


def test_list_commands_admin(client, session, admin_token, command):
    """
    Test list_commands returns all commands when requested by admin.
    """
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get("/api/commands", headers=headers)
    assert response.status_code == 200
    commands = response.get_json()
    assert any(cmd["command_id"] == command.id for cmd in commands)


def test_list_commands_not_found(client, session, admin_token):
    """
    Test list_commands returns 404 if there are no commands.
    """
    headers = {"Authorization": f"Bearer {admin_token}"}
    session.query(Command).delete()
    session.commit()
    response = client.get("/api/commands", headers=headers)
    assert response.status_code == 404
    assert "Commands not found" in response.get_json()["error"]


def test_get_command_user_own(client, session, user_token, user, command):
    """
    Test get_command returns the user's own command.
    """
    headers = {"Authorization": f"Bearer {user_token}"}
    response = client.get(f"/api/command/{command.id}", headers=headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data["id"] == command.id
    assert data["address_delivery"] == command.address_delivery


def test_get_command_user_forbidden(client, session, user_token, admin, command):
    """
    Test get_command returns 404 for a user if the command is not theirs.
    """
    # create a command for another user (already created via admin fixture)
    headers = {"Authorization": f"Bearer {user_token}"}
    response = client.get(f"/api/command/{command.id+9999}", headers=headers)
    assert response.status_code == 404


def test_get_command_admin(client, session, admin_token, command):
    """
    Test get_command returns any command for admin.
    """
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get(f"/api/command/{command.id}", headers=headers)
    assert response.status_code == 200
    assert response.get_json()["id"] == command.id


def test_create_command_missing_fields(client, user_token):
    """
    Test creating a command with missing fields returns 400.
    """
    payload = {"address_delivery": "Nowhere"}
    headers = {"Authorization": f"Bearer {user_token}"}
    response = client.post("/api/command/", json=payload, headers=headers)
    assert response.status_code == 400
    assert "Missing fields" in response.get_json()["error"]


def test_create_command_empty_products(client, user_token):
    """
    Test creating a command with no products returns 400.
    """
    payload = {"address_delivery": "Paris", "product_id": []}
    headers = {"Authorization": f"Bearer {user_token}"}
    response = client.post("/api/command/", json=payload, headers=headers)
    assert response.status_code == 400
    assert "at least one product" in response.get_json()["error"]


def test_update_command_status_missing_status(client, admin_token, command):
    """
    Test updating a command without a 'status' returns 404.
    """
    payload = {"no_status": "fail"}
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.patch(f"/api/command/{command.id}", json=payload, headers=headers)
    assert response.status_code == 404
    assert "Command status must be set" in response.get_json()["error"]


def test_update_command_status_not_found(client, admin_token):
    """
    Test updating a non-existent command returns 404.
    """
    payload = {"status": "delivered"}
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.patch("/api/command/999999", json=payload, headers=headers)
    assert response.status_code == 404
    assert "Command not found" in response.get_json()["error"]
