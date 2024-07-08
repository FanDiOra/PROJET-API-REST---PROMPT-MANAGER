from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token,jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from app.db import get_db_connection

bp = Blueprint('user', __name__)

@bp.route('/register', methods=['POST'])
def create_user_without_auth():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO user (firstname, lastname, login, password, role, groupID) VALUES (%s, %s, %s, %s, %s, %s)",
        (data['firstname'], data['lastname'], data['login'], hashed_password, data['role'], data.get('groupID'))
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'User created successfully'}), 201

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT userID, password FROM user WHERE login = %s", (data['login'],))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    if user and check_password_hash(user[1], data['password']):
        access_token = create_access_token(identity=user[0])
        return jsonify(access_token=access_token)
    return jsonify({'message': 'Invalid credentials'}), 401

# Ajoutez ici les autres routes d'administration pour la gestion des utilisateurs et des groupes
