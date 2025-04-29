import jwt
from flask import request, jsonify, g, current_app, Blueprint
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from api_ecommerce.config import SECRET_KEY
from api_ecommerce.models import User


USER_REGISTER_FIELD = ["email", "password"]
auth_print = Blueprint("auth", __name__)


@auth_print.route("/login", methods=["POST"])
def login() -> jsonify:
    """
    Authenticate a user and issue a JWT token if credentials are correct.

    Expects:
        JSON body with 'email' and 'password' fields.

    Returns:
        Response: A JSON response with a JWT token if authentication succeeds,
                  or an error message with appropriate status code if authentication fails.
    """
    data = request.get_json()

    missing_fields = list(set(USER_REGISTER_FIELD) - set(data.keys()))
    if len(missing_fields) > 0:
        return jsonify({"error": f"Missing fields : {missing_fields}"}), 400

    session = getattr(g, "db_session", None)
    if session is None:
        session_factory = getattr(current_app, "session_factory", None)
        if session_factory is None:
            return jsonify({"error": "Session factory not set"}), 500
        session = session_factory()

    user = session.query(User).filter_by(email=data["email"]).first()
    if user is None:
        return jsonify({"error": f'User {data["email"]} not exist.'}), 409

    if user.email == data["email"] and check_password_hash(
        user.password, data["password"]
    ):
        token = jwt.encode(
            {
                "user_id": user.id,
                "exp": datetime.now() + timedelta(minutes=60),
            },
            SECRET_KEY,
            algorithm="HS256",
        )
        return jsonify({"token": token})
    return jsonify({"error": "Could not verify!"}), 401


@auth_print.route("/register", methods=["POST"])
def register() -> jsonify:
    """
    Register a new user with provided email and password.

    Expects:
        JSON body with 'email' and 'password' fields.

    Returns:
        Response: A JSON response with a success message and 201 status code if registration succeeds,
                  or an error message with appropriate status code if registration fails.
    """
    data = request.get_json()

    missing_fields = list(set(USER_REGISTER_FIELD) - set(data.keys()))
    if len(missing_fields) > 0:
        return jsonify({"error": f"Missing fields : {missing_fields}"}), 400

    session = getattr(g, "db_session", None)
    if session is None:
        session_factory = getattr(current_app, "session_factory", None)
        if session_factory is None:
            return jsonify({"error": "Session factory not set"}), 500
        session = session_factory()

    if session.query(User).filter_by(email=data["email"]).first():
        return jsonify({"error": f'User {data["email"]} already exist.'}), 409

    try:
        hashed_password = generate_password_hash(
            data["password"], method="pbkdf2:sha256"
        )
        user = User(
            email=data["email"],
            password=hashed_password,
            role="user",
            name=data.get("name"),
        )
        session.add(user)
        session.commit()
    except Exception as e:
        session.rollback()
        return jsonify({"error": f"Internal error: {str(e)}"}), 500

    return jsonify({"message": "Subscription done !"}), 201
