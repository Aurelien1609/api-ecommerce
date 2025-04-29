from flask import Blueprint, jsonify, request, current_app, g
from api_ecommerce.models import Product
from datetime import datetime
from api_ecommerce.app.auth.checks import user_required

PRODUCT_FIELD = ["name", "description", "category", "price"]
products_print = Blueprint("products", __name__)


@products_print.route("/product/<int:product_id>", methods=["GET"])
def get_product(product_id: int) -> jsonify:
    """
    Retrieve the details of a single product by its ID.

    Args:
        product_id (int): The unique identifier of the product to retrieve.

    Returns:
        Response: A JSON response containing the product details if found,
                  or an error message with status code 404 if not found.
    """
    session = getattr(g, "db_session", None)
    if session is None:
        session_factory = getattr(current_app, "session_factory", None)
        if session_factory is None:
            return jsonify({"error": "Session factory not set"}), 500
        session = session_factory()
    product = session.query(Product).filter_by(id=product_id).first()
    if not product:
        return jsonify({"error": "Product not found."}), 404

    return jsonify(
        {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "category": product.category,
            "price": product.price,
            "stock": product.stock,
        }
    )


@products_print.route("/products", methods=["GET"])
def get_products() -> jsonify:
    """
    Retrieve a summary list of all products.

    Returns:
        Response: A JSON response containing a list of products,
                  each with its id and name.
    """
    session = getattr(g, "db_session", None)
    if session is None:
        session_factory = getattr(current_app, "session_factory", None)
        if session_factory is None:
            return jsonify({"error": "Session factory not set"}), 500
        session = session_factory()
    products = session.query(Product).with_entities(Product.id, Product.name).all()
    result = [{"id": prod.id, "name": prod.name} for prod in products]
    return jsonify(result)


@products_print.route("/product", methods=["POST"])
@user_required(pass_user=False, needed_admin=True)
def create_product() -> jsonify:
    """
    Create a new product with the provided data.

    Requires admin privileges.

    Returns:
        Response: A JSON response containing the details of the created product
                  and a 201 status code if successful, or an error message otherwise.
    """
    data = request.get_json()

    missing_fields = list(set(PRODUCT_FIELD) - set(data.keys()))
    if len(missing_fields) > 0:
        return jsonify({"error": f"Missing fields : {missing_fields}"}), 400

    session = getattr(g, "db_session", None)
    if session is None:
        session_factory = getattr(current_app, "session_factory", None)
        if session_factory is None:
            return jsonify({"error": "Session factory not set"}), 500
        session = session_factory()
    try:
        product = Product(
            name=data["name"],
            description=data["description"],
            category=data["category"],
            price=data["price"],
            stock=data.get("stock", 0),
            date_creation=datetime.now(),
        )
        session.add(product)
        session.commit()
    except Exception as e:
        session.rollback()
        return jsonify({"error": f"Internal error: {str(e)}"}), 500

    return (
        jsonify(
            {
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "category": product.category,
                "price": product.price,
                "stock": product.stock,
            }
        ),
        201,
    )


@products_print.route("/product/<int:product_id>", methods=["PUT"])
@user_required(pass_user=False, needed_admin=True)
def update_product(product_id: int) -> jsonify:
    """
    Update all fields of an existing product by its ID.

    Requires admin privileges.

    Args:
        product_id (int): The unique identifier of the product to update.

    Returns:
        Response: A JSON response containing the updated product details if found,
                  or an error message with status code 404 if not found.
    """

    data = request.get_json()
    session = getattr(g, "db_session", None)
    if session is None:
        session_factory = getattr(current_app, "session_factory", None)
        if session_factory is None:
            return jsonify({"error": "Session factory not set"}), 500
        session = session_factory()

    product = session.query(Product).filter_by(id=product_id).first()

    if not product:
        return jsonify({"error": "Product not found."}), 404

    for column in data.keys():
        if column in Product.__table__.columns:
            setattr(product, column, data[column])

    session.commit()

    return jsonify(
        {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "category": product.category,
            "price": product.price,
            "stock": product.stock,
        }
    )


@products_print.route("/product/<int:product_id>", methods=["DELETE"])
@user_required(pass_user=False, needed_admin=True)
def delete_product(product_id: int) -> jsonify:
    """
    Delete a product by its ID.

    Requires admin privileges.

    Args:
        product_id (int): The unique identifier of the product to delete.

    Returns:
        Response: A JSON response confirming deletion if found,
                  or an error message with status code 404 if not found.
    """
    session = getattr(g, "db_session", None)
    if session is None:
        session_factory = getattr(current_app, "session_factory", None)
        if session_factory is None:
            return jsonify({"error": "Session factory not set"}), 500
        session = session_factory()

    product = session.query(Product).filter_by(id=product_id).first()
    if not product:
        return jsonify({"error": "Product not found."}), 404

    session.delete(product)
    session.commit()
    return (
        jsonify(
            {"message": f"Product {product.name} with ID = {product_id} was deleted."}
        ),
        200,
    )
