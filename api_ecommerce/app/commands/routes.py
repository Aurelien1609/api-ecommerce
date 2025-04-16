from flask import Blueprint, jsonify, request, current_app, g
from sqlalchemy import select
from api_ecommerce.models import Command, User, CommandLign, Product
from datetime import datetime
from api_ecommerce.app.auth.checks import user_required
from api_ecommerce.app.products.routes import get_product
from collections import Counter


COMMAND_FIELD = ["address_delivery", "product_id"]
commands_print = Blueprint("commands", __name__)

@commands_print.route("/commands", methods=["GET"])
@user_required(pass_user=True, needed_admin=False)
def list_commands(user: User) -> jsonify:
    """
    Retrieve a list of commands.

    If the user is a regular user, only their commands are returned.
    If the user has higher privileges, all commands are returned.

    Args:
        user (User): The current user making the request.

    Returns:
        Response: A JSON response containing a list of commands or an error message if none are found.
    """

    session = getattr(g, "db_session", None)
    if session is None:
        session_factory = getattr(current_app, "session_factory", None)
        if session_factory is None:
            return jsonify({"error": "Session factory not set"}), 500
        session = session_factory()
    if user.role == "user":
        commands = (
            session.query(Command).filter_by(user_id=user.id).all()
        )
    else:
        commands = (
            session.query(Command).all()
        )
    if not commands:
        return jsonify({"error": "Commands not found."}), 404

    return jsonify(
        [
            {
                "command_id": command.id,
                "status": command.status,
                "address_delivery": command.address_delivery,
                "date_command": command.date_command
            }
            for command in commands
        ]
    ), 200

@commands_print.route("/command/<int:command_id>", methods=["GET"])
@user_required(pass_user=True, needed_admin=False)
def get_command(user: User, command_id: int) -> jsonify:
    """
    Retrieve the details of a specific command by its ID.

    If the user is a regular user, they can only access their own commands.
    Privileged users can access any command.

    Args:
        user (User): The current user making the request.
        command_id (int): The unique identifier of the command.

    Returns:
        Response: A JSON response with the command details or an error message if not found.
    """
    session = getattr(g, "db_session", None)
    if session is None:
        session_factory = getattr(current_app, "session_factory", None)
        if session_factory is None:
            return jsonify({"error": "Session factory not set"}), 500
        session = session_factory()
    if user.role == "user":
        command = (
            session.query(Command).filter_by(id=command_id, user_id=user.id).first()
        )
    else:
        command = (
            session.query(Command).filter_by(id=command_id).first()
        )
    if not command:
        return jsonify({"error": "Command not found."}), 404

    return jsonify(
        {
            "id": command.id,
            "status": command.status,
            "address_delivery": command.address_delivery,
            "date_command": command.date_command,
        }
    )


@commands_print.route("/command/<int:command_id>/lign", methods=["GET"])
@user_required(pass_user=True, needed_admin=False)
def get_command_lign(user: User, command_id: int) -> jsonify:
    """
    Retrieve the list of products (command lines) for a specific command.

    If the user is a regular user, they can only access their own commands.
    Privileged users can access any command.

    Args:
        user (User): The current user making the request.
        command_id (int): The unique identifier of the command.

    Returns:
        Response: A JSON response with the command's products and details, or an error message if not found.
    """
    session = getattr(g, "db_session", None)
    if session is None:
        session_factory = getattr(current_app, "session_factory", None)
        if session_factory is None:
            return jsonify({"error": "Session factory not set"}), 500
        session = session_factory()
    if user.role == "user":
        command = (
            session.query(Command).filter_by(id=command_id, user_id=user.id).first()
        )
    else:
        command = (
            session.query(Command).filter_by(id=command_id).first()
        )
    if not command:
        return jsonify({"error": "Command not found."}), 404


    stmt = (
        select(CommandLign, Product.name)
        .join(Product)
        .where(CommandLign.command_id == command_id)
    )
    commands = [
        {
            "id": command_lign.product_id,
            "name": product_name,
            "quantity": command_lign.quantity,
            "price": command_lign.price,
        }
        for command_lign, product_name in session.execute(stmt).all()
    ]
    return jsonify(
        {
            "id": command.id,
            "status": command.status,
            "products": commands,
            "address_delivery": command.address_delivery,
            "date_command": command.date_command,
        }
    )


@commands_print.route("/command/", methods=["POST"])
@user_required(pass_user=True, needed_admin=False)
def create_command(user: User) -> jsonify:
    """
    Create a new command (order) with the provided data for the current user.

    Args:
        user (User): The current user making the request.

    Returns:
        Response: A JSON response containing the new command details and a 201 status code if successful,
                  or an error message if validation fails or an error occurs.
    """
    data = request.get_json()
    missing_fields = list(set(COMMAND_FIELD) - set(data.keys()))
    if len(missing_fields) > 0:
        return jsonify({"error": f"Missing fields : {missing_fields}"}), 400

    if not isinstance(data["product_id"], list) or len(data["product_id"]) < 1:
        return (
            jsonify(
                {
                    "error": f"Command should be a list of product and contain at least one product."
                }
            ),
            400,
        )

    session = getattr(g, "db_session", None)
    if session is None:
        session_factory = getattr(current_app, "session_factory", None)
        if session_factory is None:
            return jsonify({"error": "Session factory not set"}), 500
        session = session_factory()
    try:
        command = Command(
            user_id=user.id,
            status="on hold",
            date_command=datetime.now(),
            address_delivery=data["address_delivery"],
        )
        session.add(command)
        session.commit()

        count_product = Counter(data["product_id"])

        for product_id, count in count_product.items():
            try:
                product = get_product(int(product_id)).get_json()

                if product["stock"] - count > 0:
                    command_lign = CommandLign(
                        product_id=product["id"],
                        command_id=command.id,
                        quantity=count,
                        price=product["price"],
                    )
                    session.add(command_lign)
                    session.commit()
                else:
                    return (
                        jsonify({"error": f"Product quantity is not sufficient {count} > {product["stock"]} for {product["name"]}."}),
                        500,
                    )
            except AttributeError:
                session.rollback()
                return (
                    jsonify({"error": f"Product id : {product_id} not exist."}),
                    500,
                )
    except Exception as e:
        session.rollback()
        return jsonify({"error": f"Internal error: {str(e)}"}), 500

    return (
        jsonify(
            {
                "id": command.id,
                "user_id": command.user_id,
                "date_command": command.date_command,
                "address_delivery": command.address_delivery,
            }
        ),
        201,
    )

@commands_print.route("/command/<int:command_id>", methods=["PATCH"])
@user_required(pass_user=False, needed_admin=True)
def update_command_status(command_id: int) -> jsonify:
    """
    Update only the status of a specific command by its ID.

    Requires admin privileges.

    Args:
        command_id (int): The unique identifier of the command.

    Returns:
        Response: A JSON response with the updated command details if found,
                  or an error message if not found or if the status is missing.
    """
    data = request.get_json()

    if "status" not in data.keys():
        return jsonify({"error": "Command status must be set."}), 404
    session = getattr(g, "db_session", None)
    if session is None:
        session_factory = getattr(current_app, "session_factory", None)
        if session_factory is None:
            return jsonify({"error": "Session factory not set"}), 500
        session = session_factory()
    command = (
        session.query(Command).filter_by(id=command_id).first()
    )
    if not command:
        return jsonify({"error": "Command not found."}), 404

    command.status = data["status"]
    session.commit()

    return jsonify(
        {
            "id": command.id,
            "status": command.status,
            "address_delivery": command.address_delivery,
            "date_command": command.date_command
        }
    )
