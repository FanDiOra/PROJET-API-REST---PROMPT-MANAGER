from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from app.db import get_db_connection

bp = Blueprint('user', __name__)

# ----------------------------- User Management -----------------------------------
# Create Super Admin (without authentification)
@bp.route('/register', methods=['POST'])
def create_super_admin():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO "user" (firstname, lastname, login, password, role, "groupID")
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (data['firstname'], data['lastname'], data['login'], hashed_password, data['role'], data.get('groupID'))
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'User created successfully'}), 201

# Connection
@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT "userID", password
        FROM "user"
        WHERE login = %s
        """,
        (data['login'],)
    )
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    if user and check_password_hash(user[1], data['password']):
        access_token = create_access_token(identity=user[0])
        return jsonify(access_token=access_token)
    return jsonify({'message': 'Invalid credentials'}), 401

# Create user
@bp.route('/admin/user', methods=['POST'])
@jwt_required()
def create_user():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO "user" (firstname, lastname, login, password, role, "groupID")
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (data['firstname'], data['lastname'], data['login'], hashed_password, data['role'], data.get('groupID'))
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'User created successfully'}), 201

# Get users
@bp.route('/admin/users', methods=['GET'])
@jwt_required()
def list_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT \"userID\", firstname, lastname, login, role, \"groupID\" FROM \"user\"")
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    users_list = [
        {
            'userID': user[0],
            'firstname': user[1],
            'lastname': user[2],
            'login': user[3],
            'role': user[4],
            'groupID': user[5]
        }
        for user in users
    ]
    return jsonify(users_list)

# Update user
@bp.route('/admin/user/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()
    update_fields = []
    update_values = []
    if 'firstname' in data:
        update_fields.append('firstname = %s')
        update_values.append(data['firstname'])
    if 'lastname' in data:
        update_fields.append('lastname = %s')
        update_values.append(data['lastname'])
    if 'login' in data:
        update_fields.append('login = %s')
        update_values.append(data['login'])
    if 'password' in data:
        hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
        update_fields.append('password = %s')
        update_values.append(hashed_password)
    if 'role' in data:
        update_fields.append('role = %s')
        update_values.append(data['role'])
    if 'groupID' in data:
        update_fields.append('"groupID" = %s')
        update_values.append(data['groupID'])
    update_values.append(user_id)
    cursor.execute(
        f"UPDATE \"user\" SET {', '.join(update_fields)} WHERE \"userID\" = %s",
        update_values
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'User updated successfully'})

# Delete user
@bp.route('/admin/user/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM \"user\" WHERE \"userID\" = %s", (user_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'User deleted successfully'})

