from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.db import get_db_connection

bp = Blueprint('prompt', __name__)

@bp.route('/prompt', methods=['POST'])
@jwt_required()
def create_prompt():
    data = request.get_json()
    current_user = get_jwt_identity()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO prompt (content, status, price, user_id)
        VALUES (%s, %s, %s, %s) RETURNING promptID
        """,
        (data['content'], 'en attente', data.get('price', 1000), current_user)
    )
    prompt_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'Prompt created successfully', 'promptID': prompt_id}), 201

@bp.route('/prompt/<int:prompt_id>', methods=['PUT'])
@jwt_required()
def update_prompt(prompt_id):
    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE prompt
        SET content = %s, status = %s, price = %s
        WHERE promptID = %s
        """,
        (data['content'], data['status'], data['price'], prompt_id)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'Prompt updated successfully'})

@bp.route('/prompt/<int:prompt_id>', methods=['DELETE'])
@jwt_required()
def delete_prompt(prompt_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM prompt WHERE promptID = %s", (prompt_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'Prompt deleted successfully'})

@bp.route('/prompts', methods=['GET'])
@jwt_required()
def list_prompts():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT promptID, content, status, price, creation_date, edit_date, user_id FROM prompt")
    prompts = cursor.fetchall()
    cursor.close()
    conn.close()
    prompts_list = [
        {
            'promptID': prompt[0],
            'content': prompt[1],
            'status': prompt[2],
            'price': prompt[3],
            'creation_date': prompt[4],
            'edit_date': prompt[5],
            'user_id': prompt[6]
        }
        for prompt in prompts
    ]
    return jsonify(prompts_list)

@bp.route('/user/<int:user_id>/prompts', methods=['GET'])
@jwt_required()
def list_prompts_by_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT promptID, content, status, price, creation_date, edit_date, user_id
        FROM prompt WHERE user_id = %s
        """, (user_id,))
    prompts = cursor.fetchall()
    cursor.close()
    conn.close()
    prompts_list = [
        {
            'promptID': prompt[0],
            'content': prompt[1],
            'status': prompt[2],
            'price': prompt[3],
            'creation_date': prompt[4],
            'edit_date': prompt[5],
            'user_id': prompt[6]
        }
        for prompt in prompts
    ]
    return jsonify(prompts_list)
