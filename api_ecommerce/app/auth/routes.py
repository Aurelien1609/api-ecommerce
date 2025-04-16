import jwt
from flask import Blueprint, jsonify, request, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from api_ecommerce.config import SECRET_KEY
from api_ecommerce.models import engine, User
from sqlalchemy.orm import sessionmaker


auth_print = Blueprint('auth', __name__)

@auth_print.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    with sessionmaker(bind=engine)() as session:
        user = session.query(User).filter_by(email=data["email"]).first()
        print(user.password, user.name, user.role, user.email)
        print(check_password_hash(user.password, data["password"]))
    # auth = request.authorization

    # if auth and auth.username == 'admin' and auth.password == 'password123':
    #     token = jwt.encode(
    #         {
    #             'user': auth.username,
    #             'exp': datetime.now() + timedelta(minutes=60)
    #         },
    #             SECRET_KEY, algorithm="HS256")
    #     return jsonify({'token': token})

    return make_response('Could not verify!', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})

@auth_print.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
    data["password"] = hashed_password
    with sessionmaker(bind=engine)() as session:
        session.add(User(**data))
        session.commit()
    return jsonify({'message': 'Registered successfully!'})