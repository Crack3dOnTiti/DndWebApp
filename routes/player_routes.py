from flask import Blueprint, jsonify, request, session as flask_session
import sys
import os
import random

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'database'))
from models import SessionLocal, Player, PlayerStats

player_bp = Blueprint('players', __name__, url_prefix='/api/players')

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

def apply_origin_modifiers(base_stats, origin):
    """Apply stat modifiers based on character origin"""
    modifiers = {
        'vif': {'str_stat': -15, 'spd_stat': 10, 'stm_stat': 10, 'mny_stat': 0.0},  # MNY stays 1.0
        'martial': {'str_stat': 20, 'spd_stat': -5, 'mny_stat': 0.2},  # MNY becomes 1.2
        'hommedefoie': {'str_stat': -10, 'spd_stat': -5, 'stm_stat': 20, 'mny_stat': -0.2},  # MNY becomes 0.8
        'mediateur': {'luk_stat': 5, 'mny_stat': 0.5}  # MNY becomes 1.5
    }
    
    if origin in modifiers:
        origin_mods = modifiers[origin]
        for stat, modifier in origin_mods.items():
            if stat in base_stats:
                if stat == 'mny_stat':
                    base_stats[stat] += modifier  # Add to 1.0 base
                else:
                    base_stats[stat] += modifier  # Add to 10 base
    
    return base_stats

@player_bp.route('', methods=['GET', 'POST'])
def handle_players():
    db_session = SessionLocal()
    try:
        if request.method == 'GET':
            players = db_session.query(Player).all()
            player_list = []
            for player in players:
                player_list.append({
                    "id": player.id,
                    "name": player.name,
                    "title": player.title,
                    "current_hp": player.current_hp,
                    "max_hp": player.max_hp,
                    "current_stam": player.current_stam,
                    "max_stam": player.max_stam,
                    "sin": player.sin,
                    "virtue": player.virtue,
                    "general_feeling": player.general_feeling,
                    "skill_name": player.skill_name,
                    "skill_description": player.skill_description,
                    "passive_name": player.passive_name,
                    "passive_description": player.passive_description,
                    "starter_background": player.starter_background,
                    "age": player.age,
                    "gender": player.gender,
                    "temperature": player.temperature,
                    "saturation": player.saturation,
                    "biology": player.biology,
                    "main_style": player.main_style,
                    "ritual": player.ritual,
                    "last_d5_roll": player.last_d5_roll,
                    "last_d10_roll": player.last_d10_roll,
                    "last_d20_roll": player.last_d20_roll,
                    "last_d100_roll": player.last_d100_roll
                })
            return jsonify(player_list)
            
        elif request.method == 'POST':
            data = request.get_json()
            
            # Base stats (defaults)
            base_stats = {
                'str_stat': 10,
                'stm_stat': 10, 
                'spd_stat': 10,
                'luk_stat': 10,
                'mny_stat': 1.0
            }
            
            # Apply origin modifiers to stats
            origin = data.get('starter_background')
            if origin:
                final_stats = apply_origin_modifiers(base_stats, origin)
            else:
                final_stats = base_stats
            
            # Create the player record
            new_player = Player(
                name=data.get('name'),
                title=data.get('title'),
                current_hp=data.get('current_hp', 100.0),
                max_hp=data.get('max_hp', 100.0),
                current_stam=data.get('current_stam', 100.0),
                max_stam=data.get('max_stam', 100.0),
                sin=data.get('sin'),
                virtue=data.get('virtue'),
                general_feeling=data.get('general_feeling'),
                skill_name=data.get('skill_name'),
                skill_description=data.get('skill_description'),
                passive_name=data.get('passive_name'),
                passive_description=data.get('passive_description'),
                starter_background=data.get('starter_background'),
                age=data.get('age'),
                gender=data.get('gender'),
                temperature=data.get('temperature'),
                saturation=data.get('saturation'),
                biology=data.get('biology'),
                main_style=data.get('main_style'),
                ritual=data.get('ritual')
            )
            db_session.add(new_player)
            db_session.flush()  # Get the player ID
            
            # Create the stats record linked to the player
            new_stats = PlayerStats(
                player_id=new_player.id,
                str_stat=final_stats['str_stat'],
                stm_stat=final_stats['stm_stat'],
                spd_stat=final_stats['spd_stat'],
                luk_stat=final_stats['luk_stat'],
                mny_stat=final_stats['mny_stat']
            )
            db_session.add(new_stats)
            db_session.commit()
            db_session.refresh(new_player)
            
            # Store in Flask session for authentication
            flask_session['player_id'] = new_player.id
            flask_session['player_name'] = new_player.name
            
            return jsonify({
                "message": "Player created successfully", 
                "id": new_player.id,
                "stats_applied": final_stats
            }), 201
            
    except Exception as e:
        db_session.rollback()
        return handle_database_error(e)
    finally:
        db_session.close()

@player_bp.route('/<int:player_id>', methods=['GET', 'DELETE'])
def handle_player_by_id(player_id):
    db_session = SessionLocal()
    try:
        player = db_session.query(Player).filter(Player.id == player_id).first()
        if not player:
            return jsonify({"error": "Player not found"}), 404
            
        if request.method == 'GET':
            player_data = {
                "id": player.id,
                "name": player.name,
                "title": player.title,
                "current_hp": player.current_hp,
                "max_hp": player.max_hp,
                "current_stam": player.current_stam,
                "max_stam": player.max_stam,
                "sin": player.sin,
                "virtue": player.virtue,
                "general_feeling": player.general_feeling,
                "skill_name": player.skill_name,
                "skill_description": player.skill_description,
                "passive_name": player.passive_name,
                "passive_description": player.passive_description,
                "starter_background": player.starter_background,
                "age": player.age,
                "gender": player.gender,
                "temperature": player.temperature,
                "saturation": player.saturation,
                "biology": player.biology,
                "main_style": player.main_style,
                "ritual": player.ritual,
                "last_d5_roll": player.last_d5_roll,
                "last_d10_roll": player.last_d10_roll,
                "last_d20_roll": player.last_d20_roll,
                "last_d100_roll": player.last_d100_roll
            }
            return jsonify(player_data)
            
        elif request.method == 'DELETE':
            db_session.delete(player)
            db_session.commit()
            return jsonify({"message": f"Player with id {player_id} deleted successfully"}), 200
        
    except Exception as e:
        db_session.rollback()
        return handle_database_error(e)
    finally:
        db_session.close()

# PLAYER-ONLY ENDPOINTS (limited fields they can modify)
@player_bp.route('/<int:player_id>/update-self', methods=['PUT'])
def player_update_self(player_id):
    """Allow players to update only their allowed fields"""
    db_session = SessionLocal()
    try:
        player = db_session.query(Player).filter(Player.id == player_id).first()
        if not player:
            return jsonify({"error": "Player not found"}), 404
            
        data = request.get_json()
        
        # Only allow players to update these fields
        allowed_fields = ['name', 'skill_name', 'skill_description', 'starter_background', 'gender']
        
        for field in allowed_fields:
            if field in data:
                setattr(player, field, data[field])
        
        db_session.commit()
        return jsonify({"message": "Player updated successfully"}), 200
        
    except Exception as e:
        db_session.rollback()
        return handle_database_error(e)
    finally:
        db_session.close()

# DICE ROLLING ENDPOINTS (players can roll their own dice)
@player_bp.route('/<int:player_id>/roll/<string:dice_type>', methods=['POST'])
def roll_dice(player_id, dice_type):
    """Roll dice and update player's last roll for that dice type"""
    db_session = SessionLocal()
    try:
        player = db_session.query(Player).filter(Player.id == player_id).first()
        if not player:
            return jsonify({"error": "Player not found"}), 404
            
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
            player.last_d5_roll = result
        elif dice_type == 'd10':
            player.last_d10_roll = result
        elif dice_type == 'd20':
            player.last_d20_roll = result
        elif dice_type == 'd100':
            player.last_d100_roll = result
            
        db_session.commit()
        
        # TODO: Broadcast this roll via WebSocket to all connected clients
        
        return jsonify({
            "message": f"Rolled {dice_type}",
            "result": result,
            "player_name": player.name,
            "dice_type": dice_type
        }), 200
        
    except Exception as e:
        db_session.rollback()
        return handle_database_error(e)
    finally:
        db_session.close()

# HOST-ONLY ENDPOINTS (full admin control)
@player_bp.route('/<int:player_id>/host-update', methods=['PUT'])
def host_update_player(player_id):
    """Allow host to update ANY field on a player"""
    db_session = SessionLocal()
    try:
        player = db_session.query(Player).filter(Player.id == player_id).first()
        if not player:
            return jsonify({"error": "Player not found"}), 404
            
        data = request.get_json()
        
        # Host can update any field
        updatable_fields = [
            'current_hp', 'max_hp', 'current_stam', 'max_stam', 'name', 'title',
            'sin', 'virtue', 'general_feeling', 'skill_name', 'skill_description',
            'passive_name', 'passive_description', 'starter_background', 'age',
            'gender', 'temperature', 'saturation', 'biology', 'main_style', 'ritual'
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(player, field, data[field])
        
        db_session.commit()
        
        # TODO: Broadcast changes via WebSocket to all connected clients
        
        return jsonify({"message": "Player updated by host successfully"}), 200
        
    except Exception as e:
        db_session.rollback()
        return handle_database_error(e)
    finally:
        db_session.close()