from flask import Blueprint, jsonify, request
import sys
import os
import random

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'database'))
from models import SessionLocal, NPC

npc_bp = Blueprint('npcs', __name__, url_prefix='/api/npcs')

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

@npc_bp.route('', methods=['GET', 'POST'])
def handle_npcs():
    session = SessionLocal()
    try:
        if request.method == 'GET':
            npcs = session.query(NPC).all()
            npc_list = []
            for npc in npcs:
                npc_list.append({
                    "id": npc.id,
                    "name": npc.name,
                    "title": npc.title,
                    "current_hp": npc.current_hp,
                    "max_hp": npc.max_hp,
                    "current_stam": npc.current_stam,
                    "max_stam": npc.max_stam,
                    "sin": npc.sin,
                    "virtue": npc.virtue,
                    "skill_name": npc.skill_name,
                    "skill_description": npc.skill_description,
                    "age": npc.age,
                    "gender": npc.gender,
                    "biology": npc.biology,
                    "main_style": npc.main_style,
                    "ritual": npc.ritual,
                    "last_d5_roll": npc.last_d5_roll,
                    "last_d10_roll": npc.last_d10_roll,
                    "last_d20_roll": npc.last_d20_roll,
                    "last_d100_roll": npc.last_d100_roll
                })
            return jsonify(npc_list)
            
        elif request.method == 'POST':
            data = request.get_json()
            new_npc = NPC(
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
            session.add(new_npc)
            session.commit()
            session.refresh(new_npc)
            return jsonify({"message": "NPC created successfully", "id": new_npc.id}), 201
            
    except Exception as e:
        session.rollback()
        return handle_database_error(e)
    finally:
        session.close()

@npc_bp.route('/<int:npc_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_npc_by_id(npc_id):
    session = SessionLocal()
    try:
        npc = session.query(NPC).filter(NPC.id == npc_id).first()
        if not npc:
            return jsonify({"error": "NPC not found"}), 404
            
        if request.method == 'GET':
            npc_data = {
                "id": npc.id,
                "name": npc.name,
                "title": npc.title,
                "current_hp": npc.current_hp,
                "max_hp": npc.max_hp,
                "current_stam": npc.current_stam,
                "max_stam": npc.max_stam,
                "sin": npc.sin,
                "virtue": npc.virtue,
                "skill_name": npc.skill_name,
                "skill_description": npc.skill_description,
                "age": npc.age,
                "gender": npc.gender,
                "biology": npc.biology,
                "main_style": npc.main_style,
                "ritual": npc.ritual,
                "last_d5_roll": npc.last_d5_roll,
                "last_d10_roll": npc.last_d10_roll,
                "last_d20_roll": npc.last_d20_roll,
                "last_d100_roll": npc.last_d100_roll
            }
            return jsonify(npc_data)
            
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
                    setattr(npc, field, data[field])
            
            session.commit()
            return jsonify({"message": "NPC updated successfully"}), 200
            
        elif request.method == 'DELETE':
            session.delete(npc)
            session.commit()
            return jsonify({"message": f"NPC with id {npc_id} deleted successfully"}), 200
        
    except Exception as e:
        session.rollback()
        return handle_database_error(e)
    finally:
        session.close()

# HOST DICE ROLLING FOR NPCS
@npc_bp.route('/<int:npc_id>/roll/<string:dice_type>', methods=['POST'])
def roll_npc_dice(npc_id, dice_type):
    """Host rolls dice for NPCs"""
    session = SessionLocal()
    try:
        npc = session.query(NPC).filter(NPC.id == npc_id).first()
        if not npc:
            return jsonify({"error": "NPC not found"}), 404
            
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
            npc.last_d5_roll = result
        elif dice_type == 'd10':
            npc.last_d10_roll = result
        elif dice_type == 'd20':
            npc.last_d20_roll = result
        elif dice_type == 'd100':
            npc.last_d100_roll = result
            
        session.commit()
        
        # TODO: Broadcast this roll via WebSocket to all connected clients
        
        return jsonify({
            "message": f"Rolled {dice_type} for NPC",
            "result": result,
            "npc_name": npc.name,
            "dice_type": dice_type
        }), 200
        
    except Exception as e:
        session.rollback()
        return handle_database_error(e)
    finally:
        session.close()