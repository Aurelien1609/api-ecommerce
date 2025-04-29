import jwt
from flask import request, jsonify, current_app
from api_ecommerce.models import User
from api_ecommerce.config import SECRET_KEY
from functools import wraps


def user_required(pass_user: bool = False, needed_admin: bool = True):
    """
    Decorator to enforce authentication and (optionally) admin authorization for route handlers.

    This decorator validates a JWT token from the 'Authorization' header, fetches the current user,
    and verifies their permissions. It can either pass the user object as an argument to the route handler
    or not, depending on the 'pass_user' parameter.

    Args:
        pass_user (bool): If True, passes the User object as the first argument to the decorated function.
        needed_admin (bool): If True, restricts access to users with admin privileges only.

    Returns:
        Callable: The decorated function with authentication and authorization checks applied.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            auth_header = request.headers.get("Authorization", None)
            if not auth_header or not auth_header.startswith("Bearer "):
                return jsonify({"message": "Token missing"}), 401
            token = auth_header.split(" ")[1]
            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
                user_id = payload.get("user_id")
                if not user_id:
                    return jsonify({"message": "Token invalid : user_id missing."}), 401
            except jwt.ExpiredSignatureError:
                return jsonify({"message": "Token expired"}), 401
            except jwt.InvalidTokenError:
                return jsonify({"message": "Token invalid"}), 401

            with getattr(current_app, "session_factory", None)() as session:
                user = session.query(User).filter_by(id=user_id).first()
                if not user:
                    return jsonify({"message": "User not found."}), 404
                if needed_admin and not user.role == "admin":
                    return jsonify({"message": "Admin role is required."}), 403
                if pass_user:
                    return func(user, *args, **kwargs)
                else:
                    return func(*args, **kwargs)

        return wrapper

    return decorator
