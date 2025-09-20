from flask import Blueprint, jsonify, request
import sys
import os
import random

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'database'))
from models import SessionLocal, Enemy

enemy_bp = Blueprint('enemies', __name__, url_prefix='/api/enemies')

def handle_database_error(e):
    error_response = {
        "detail": [
            {
                "loc": ["query"],
                "msg": str(e),
                "type": "database_error"
            }
        ]
    }
    return jsonify(error_response), 422

@enemy_bp.route('', methods=['GET', 'POST'])
def handle_enemies():
    session = SessionLocal()
    try:
        if request.method == 'GET':
            enemies = session.query(Enemy).all()
            enemy_list = []
            for enemy in enemies:
                enemy_list.append({
                    "id": enemy.id,
                    "name": enemy.name,
                    "title": enemy.title,
                    "current_hp": enemy.current_hp,
                    "max_hp": enemy.max_hp,
                    "current_stam": enemy.current_stam,
                    "max_stam": enemy.max_stam,
                    "sin": enemy.sin,
                    "virtue": enemy.virtue,
                    "skill_name": enemy.skill_name,
                    "skill_description": enemy.skill_description,
                    "age": enemy.age,
                    "gender": enemy.gender,
                    "biology": enemy.biology,
                    "main_style": enemy.main_style,
                    "ritual": enemy.ritual,
                    "last_d5_roll": enemy.last_d5_roll,
                    "last_d10_roll": enemy.last_d10_roll,
                    "last_d20_roll": enemy.last_d20_roll,
                    "last_d100_roll": enemy.last_d100_roll
                })
            return jsonify(enemy_list)
            
        elif request.method == 'POST':
            data = request.get_json()
            new_enemy = Enemy(
                name=data.get('name'),
                title=data.get('title'),
                current_hp=data.get('current_hp', 100.0),
                max_hp=data.get('max_hp', 100.0),
                current_stam=data.get('current_stam', 100.0),
                max_stam=data.get('max_stam', 100.0),
                sin=data.get('sin'),
                virtue=data.get('virtue'),
                skill_name=data.get('skill_name'),
                skill_description=data.get('skill_description'),
                age=data.get('age'),
                gender=data.get('gender'),
                biology=data.get('biology'),
                main_style=data.get('main_style'),
                ritual=data.get('ritual')
            )
            session.add(new_enemy)
            session.commit()
            session.refresh(new_enemy)
            return jsonify({"message": "Enemy created successfully", "id": new_enemy.id}), 201
            
    except Exception as e:
        session.rollback()
        return handle_database_error(e)
    finally:
        session.close()

@enemy_bp.route('/<int:enemy_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_enemy_by_id(enemy_id):
    session = SessionLocal()
    try:
        enemy = session.query(Enemy).filter(Enemy.id == enemy_id).first()
        if not enemy:
            return jsonify({"error": "Enemy not found"}), 404
            
        if request.method == 'GET':
            enemy_data = {
                "id": enemy.id,
                "name": enemy.name,
                "title": enemy.title,
                "current_hp": enemy.current_hp,
                "max_hp": enemy.max_hp,
                "current_stam": enemy.current_stam,
                "max_stam": enemy.max_stam,
                "sin": enemy.sin,
                "virtue": enemy.virtue,
                "skill_name": enemy.skill_name,
                "skill_description": enemy.skill_description,
                "age": enemy.age,
                "gender": enemy.gender,
                "biology": enemy.biology,
                "main_style": enemy.main_style,
                "ritual": enemy.ritual,
                "last_d5_roll": enemy.last_d5_roll,
                "last_d10_roll": enemy.last_d10_roll,
                "last_d20_roll": enemy.last_d20_roll,
                "last_d100_roll": enemy.last_d100_roll
            }
            return jsonify(enemy_data)
            
        elif request.method == 'PUT':
            data = request.get_json()
            
            # Host can update any field
            updatable_fields = [
                'current_hp', 'max_hp', 'current_stam', 'max_stam', 'name', 'title',
                'sin', 'virtue', 'skill_name', 'skill_description',
                'age', 'gender', 'biology', 'main_style', 'ritual'
            ]
            
            for field in updatable_fields:
                if field in data:
                    setattr(enemy, field, data[field])
            
            session.commit()
            return jsonify({"message": "Enemy updated successfully"}), 200
            
        elif request.method == 'DELETE':
            session.delete(enemy)
            session.commit()
            return jsonify({"message": f"Enemy with id {enemy_id} deleted successfully"}), 200
        
    except Exception as e:
        session.rollback()
        return handle_database_error(e)
    finally:
        session.close()

# HOST DICE ROLLING FOR ENEMIES
@enemy_bp.route('/<int:enemy_id>/roll/<string:dice_type>', methods=['POST'])
def roll_enemy_dice(enemy_id, dice_type):
    """Host rolls dice for enemies"""
    session = SessionLocal()
    try:
        enemy = session.query(Enemy).filter(Enemy.id == enemy_id).first()
        if not enemy:
            return jsonify({"error": "Enemy not found"}), 404
            
        # Determine dice range
        dice_map = {
            'd5': 5,
            'd10': 10,
            'd20': 20,
            'd100': 100
        }
        
        if dice_type not in dice_map:
            return jsonify({"error": "Invalid dice type. Use d5, d10, d20, or d100"}), 400
            
        # Roll the dice
        result = random.randint(1, dice_map[dice_type])
        
        # Update the appropriate last roll field
        if dice_type == 'd5':
            enemy.last_d5_roll = result
        elif dice_type == 'd10':
            enemy.last_d10_roll = result
        elif dice_type == 'd20':
            enemy.last_d20_roll = result
        elif dice_type == 'd100':
            enemy.last_d100_roll = result
            
        session.commit()
        
        # TODO: Broadcast this roll via WebSocket to all connected clients
        
        return jsonify({
            "message": f"Rolled {dice_type} for enemy",
            "result": result,
            "enemy_name": enemy.name,
            "dice_type": dice_type
        }), 200
        
    except Exception as e:
        session.rollback()
        return handle_database_error(e)
    finally:
        session.close()