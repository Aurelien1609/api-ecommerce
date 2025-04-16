import pytest
from api_ecommerce.models import Product
from datetime import datetime

@pytest.fixture
def product_in_db(session):
    """
    Fixture: Create a product in the database for product tests.
    Returns:
        Product instance
    """
    product = Product(
        name="TestProduct",
        description="A test description",
        category="Testing",
        price=42.0,
        stock=10,
        date_creation=datetime(2024, 1, 1)
    )
    session.add(product)
    session.commit()
    return product


@pytest.fixture
def admin_token(client, session):
    """
    Fixture: Create an admin user and return a valid JWT token for authentication.
    """
    email = "admin@hotmail.com"
    password = "admin"
    payload = {"email": email, "password": password}
    response = client.post("/api/auth/login", json=payload)
    return response.get_json()["token"]

def test_get_product_success(client, session, product_in_db):
    """
    Test retrieving a product by its ID.
    Expects:
        - Status code 200 (OK)
        - Correct product information in response
    """
    response = client.get(f"/api/product/{product_in_db.id}")
    assert response.status_code == 200
    json = response.get_json()
    assert json["id"] == product_in_db.id
    assert json["name"] == product_in_db.name

def test_get_product_not_found(client):
    """
    Test retrieving a product that does not exist.
    Expects:
        - Status code 404 (Not Found)
        - Proper error message in response
    """
    response = client.get("/api/product/99999")
    assert response.status_code == 404
    assert "Product not found" in response.get_json().get("error", "")

def test_get_products_list(client, session, product_in_db):
    """
    Test retrieving a list of all products.
    Expects:
        - Status code 200 (OK)
        - Response contains a list with at least one product
    """
    response = client.get("/api/products")
    assert response.status_code == 200
    json = response.get_json()
    assert isinstance(json, list)
    assert any(prod["id"] == product_in_db.id for prod in json)

def test_create_product_success(client, session, admin_token):
    """
    Test creating a new product with valid data (admin required).
    Expects:
        - Status code 201 (Created)
        - Product details in response
    """
    payload = {
        "name": "Banana",
        "description": "Yellow fruit",
        "category": "Fruits",
        "price": 1.99,
        "stock": 25
    }
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.post("/api/product", json=payload, headers=headers)
    print(response.text)
    assert response.status_code == 201
    data = response.get_json()
    assert data["name"] == payload["name"]
    assert data["category"] == payload["category"]

def test_create_product_missing_fields(client, admin_token):
    """
    Test creating a product with missing required fields.
    Expects:
        - Status code 400 (Bad Request)
        - Proper error message in response
    """
    payload = {"name": "Apple"}
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.post("/api/product", json=payload, headers=headers)
    assert response.status_code == 400
    assert "Missing fields" in response.get_json()["error"]

def test_update_product_success(client, session, product_in_db, admin_token):
    """
    Test updating all fields of an existing product.
    Expects:
        - Status code 200 (OK)
        - Updated product information in response
    """
    update = {
        "name": "UpdatedName",
        "description": "New description",
        "category": "NewCat",
        "price": 999.0,
        "stock": 50
    }
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.put(f"/api/product/{product_in_db.id}", json=update, headers=headers)
    assert response.status_code == 200
    data = response.get_json()
    for field in update:
        assert data[field] == update[field]

def test_update_product_not_found(client, admin_token):
    """
    Test updating a product that does not exist.
    Expects:
        - Status code 404 (Not Found)
        - Proper error message in response
    """
    update = {"name": "Whatever", "description": "desc", "category": "cat", "price": 2.2}
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.put("/api/product/99999", json=update, headers=headers)
    assert response.status_code == 404
    assert "Product not found" in response.get_json()["error"]

def test_delete_product_success(client, session, product_in_db, admin_token):
    """
    Test deleting a product by ID.
    Expects:
        - Status code 200 (OK)
        - Confirmation message in response
    """
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.delete(f"/api/product/{product_in_db.id}", headers=headers)
    assert response.status_code == 200
    msg = response.get_json()["message"]
    assert str(product_in_db.id) in msg

def test_delete_product_not_found(client, admin_token):
    """
    Test deleting a product that does not exist.
    Expects:
        - Status code 404 (Not Found)
        - Proper error message in response
    """
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.delete("/api/product/99999", headers=headers)
    assert response.status_code == 404
    assert "Product not found" in response.get_json()["error"]