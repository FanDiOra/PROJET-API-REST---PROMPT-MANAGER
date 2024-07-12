from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.db import get_db_connection

bp = Blueprint('prompt', __name__)

# ----------------------------- Prompt Management -----------------------------------
# Create
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
        (data['content'], 'on hold', 1000, current_user)
    )
    prompt_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'Prompt created successfully', 'promptID': prompt_id}), 201

# Update
@bp.route('/prompt/<int:prompt_id>', methods=['PUT'])
@jwt_required()
def update_prompt(prompt_id):
    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE prompt
        SET content = %s, status = 'on hold', price = %s
        WHERE promptID = %s
        """,
        (data['content'], data.get['price', 1000], prompt_id)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'Prompt updated successfully'})

# Validate
@bp.route('/prompt/<int:prompt_id>/validate', methods=['PUT'])
@jwt_required()
def validate_prompt(prompt_id):
    data = request.get_json()
    action = data.get('action')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if action == 'valid':
        cursor.execute("UPDATE prompt SET status = 'activated' WHERE promptID = %s", (prompt_id,))
    elif action == 'to_modify':
        cursor.execute("UPDATE prompt SET status = 'to review' WHERE promptID = %s", (prompt_id,))
    else:
        return jsonify({'message': 'Invalid action'}), 400
    
    conn.commit()
    cursor.close()
    conn.close()
    
    return jsonify({'message': 'Prompt status updated successfully'})

# Vote
@bp.route('/prompt/<int:prompt_id>/vote', methods=['POST'])
@jwt_required()
def vote_prompt(prompt_id):
    data = request.get_json()
    current_user = get_jwt_identity()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO vote (vote_value, user_id, prompt_id) VALUES (%s, %s, %s)",
        (data['vote_value'], current_user, prompt_id)
    )
    conn.commit()
    cursor.close()
    
    # Vérifier si le nombre de votes positifs atteint le seuil pour activer le prompt
    cursor = conn.cursor()
    cursor.execute(
        "SELECT SUM(vote_value) FROM vote WHERE prompt_id = %s", (prompt_id,)
    )
    total_votes = cursor.fetchone()[0]
    if total_votes >= 6: 
        cursor.execute(
            "UPDATE prompt SET status = 'activated' WHERE promptID = %s", (prompt_id,)
        )
        conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'message': 'Vote recorded successfully'})

# Note
@bp.route('/prompt/<int:prompt_id>/note', methods=['POST'])
@jwt_required()
def note_prompt(prompt_id):
    data = request.get_json()
    current_user = get_jwt_identity()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO note (note_value, user_id, prompt_id) VALUES (%s, %s, %s)",
        (data['note_value'], current_user, prompt_id)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'Prompt noted successfully'})

# Delete
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

# List
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

# List by user
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
