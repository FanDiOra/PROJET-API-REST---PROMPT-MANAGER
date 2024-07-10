from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.db import get_db_connection

bp = Blueprint('group', __name__)

# ----------------------------- Group Management -----------------------------------
# Create
@bp.route('/admin/group', methods=['POST'])
@jwt_required()
def create_group():
    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO \"group\" (name) VALUES (%s) RETURNING \"groupID\"",
        (data['name'],)
    )
    group_id = cursor.fetchone()[0]
    if 'user_ids' in data:
        for user_id in data['user_ids']:
            cursor.execute("UPDATE \"user\" SET \"groupID\" = %s WHERE \"userID\" = %s", (group_id, user_id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'Group created successfully', 'groupID': group_id}), 201

# Update
@bp.route('/admin/group/<int:group_id>', methods=['PUT'])
@jwt_required()
def update_group(group_id):
    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE \"group\" SET name = %s WHERE \"groupID\" = %s", (data['name'], group_id))
    cursor.execute("UPDATE \"user\" SET \"groupID\" = NULL WHERE \"groupID\" = %s", (group_id,))
    if 'user_ids' in data:
        for user_id in data['user_ids']:
            cursor.execute("UPDATE \"user\" SET \"groupID\" = %s WHERE \"userID\" = %s", (group_id, user_id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'Group updated successfully'})

# List
@bp.route('/admin/groups', methods=['GET'])
@jwt_required()
def list_groups():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT \"groupID\", name FROM \"group\"")
    groups = cursor.fetchall()
    cursor.close()
    conn.close()
    groups_list = [
        {
            'groupID': group[0],
            'name': group[1]
        }
        for group in groups
    ]
    return jsonify(groups_list)

# List users by group
@bp.route('/admin/group/<int:group_id>', methods=['GET'])
@jwt_required()
def get_group(group_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT \"groupID\", name FROM \"group\" WHERE \"groupID\" = %s", (group_id,))
    group = cursor.fetchone()
    cursor.execute("SELECT \"userID\", firstname, lastname FROM \"user\" WHERE \"groupID\" = %s", (group_id,))
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    if group is None:
        return jsonify({'message': 'Group not found'}), 404
    group_info = {
        'groupID': group[0],
        'name': group[1],
        'users': [{'userID': user[0], 'firstname': user[1], 'lastname': user[2]} for user in users]
    }
    return jsonify(group_info)

# Delete
@bp.route('/admin/group/<int:group_id>', methods=['DELETE'])
@jwt_required()
def delete_group(group_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE \"user\" SET \"groupID\" = NULL WHERE \"groupID\" = %s", (group_id,))
    cursor.execute("DELETE FROM \"group\" WHERE \"groupID\" = %s", (group_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'Group deleted successfully'})
