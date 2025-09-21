from flask import Flask, jsonify, render_template, session, redirect, request
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
from datetime import datetime
import secrets
import os
from dotenv import load_dotenv
from routes.player_routes import player_bp
from routes.enemy_routes import enemy_bp
from routes.npc_routes import npc_bp

load_dotenv()

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")
app.secret_key = secrets.token_hex(16)

# Register blueprints
app.register_blueprint(player_bp)
app.register_blueprint(enemy_bp)
app.register_blueprint(npc_bp)

# Store connected clients
connected_clients = {
    'host': None,
    'players': {}
}

@app.route('/api/test')
def test_endpoint():
    return jsonify({"message": "D&D API is working!"})

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/character-creation')
def character_creation():
    return render_template('player_creation.html')

@app.route('/player-dashboard/<int:player_id>')
def player_dashboard(player_id):
    if 'player_id' not in session or session['player_id'] != player_id:
        return redirect('/')
    return render_template('player_dashboard.html')

@app.route('/host-login', methods=['POST'])
def host_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    # Use same credentials as database
    db_user = os.getenv('POSTGRES_USER')
    db_password = os.getenv('POSTGRES_PASSWORD')
    
    if username == db_user and password == db_password:
        session['is_host'] = True
        return jsonify({"success": True}), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401

@app.route('/host-dashboard')
def host_dashboard():
    if 'is_host' not in session or not session['is_host']:
        return redirect('/')
    return render_template('host_dashboard.html')

# WebSocket Events
@socketio.on('connect')
def handle_connect():
    print(f"Client connected: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    print(f"Client disconnected: {request.sid}")
    # Remove from connected clients
    if connected_clients['host'] == request.sid:
        connected_clients['host'] = None
    # Remove from players
    for player_id, sid in list(connected_clients['players'].items()):
        if sid == request.sid:
            del connected_clients['players'][player_id]
            break

@socketio.on('join_game')
def handle_join_game(data):
    """Join a user to their appropriate room"""
    user_type = data.get('user_type')  # 'host' or 'player'
    user_id = data.get('user_id')
    user_name = data.get('user_name', 'Unknown')
    
    if user_type == 'host':
        join_room('host_room')
        connected_clients['host'] = request.sid
        emit('join_success', {
            'message': 'Host connected',
            'user_type': 'host'
        })
        print(f"Host connected: {request.sid}")
        
    elif user_type == 'player':
        player_room = f'player_{user_id}'
        join_room(player_room)
        join_room('all_players')
        connected_clients['players'][user_id] = request.sid
        emit('join_success', {
            'message': f'Player {user_name} connected',
            'user_type': 'player',
            'player_id': user_id
        })
        print(f"Player {user_name} (ID: {user_id}) connected: {request.sid}")

@socketio.on('send_message')
def handle_message(data):
    """Handle message sending between host and players"""
    sender_type = data.get('sender_type')  # 'host' or 'player'
    message = data.get('message', '').strip()
    voice_mode = data.get('voice_mode', 'host')  # 'host' or 'mystery'
    sender_name = data.get('sender_name', 'Unknown')
    
    if not message:
        return
    
    # Determine message styling based on voice mode
    is_mystery = voice_mode == 'mystery' or voice_mode == '???'
    message_class = 'mystery-message' if is_mystery else 'normal-message'
    
    message_data = {
        'sender_name': sender_name,
        'sender_type': sender_type,
        'message': message,
        'voice_mode': voice_mode,
        'message_class': message_class,
        'timestamp': datetime.now().strftime('%H:%M'),
        'is_mystery': is_mystery
    }
    
    if sender_type == 'host':
        # Host sending to players
        target_players = data.get('target_players', [])
        if target_players:
            for player_id in target_players:
                player_room = f'player_{player_id}'
                emit('new_message', message_data, room=player_room)
            
            # Send confirmation to host
            emit('message_sent', {
                **message_data,
                'targets': target_players,
                'target_count': len(target_players)
            }, room='host_room')
        else:
            # No players selected
            emit('message_error', {
                'error': 'Aucun joueur sélectionné'
            }, room='host_room')
        
    elif sender_type == 'player':
        # Player sending to host
        player_id = data.get('player_id')
        message_data['player_id'] = player_id
        emit('new_message', message_data, room='host_room')

@socketio.on('update_player_stats')
def handle_player_stats_update(data):
    """Handle real-time player stat updates from combat manager"""
    player_id = data.get('player_id')
    stat_type = data.get('stat_type')  # 'hp' or 'stamina'
    current_value = data.get('current_value')
    max_value = data.get('max_value')
    
    # Broadcast to all connected clients
    update_data = {
        'player_id': player_id,
        'stat_type': stat_type,
        'current_value': current_value,
        'max_value': max_value,
        'timestamp': datetime.now().strftime('%H:%M:%S')
    }
    
    # Send to host
    emit('player_stats_updated', update_data, room='host_room')
    
    # Send to specific player
    player_room = f'player_{player_id}'
    emit('stats_updated', update_data, room=player_room)

@socketio.on('dice_roll_broadcast')
def handle_dice_roll_broadcast(data):
    """Broadcast dice rolls to all connected clients"""
    roller_type = data.get('roller_type')  # 'host' or 'player'
    roller_name = data.get('roller_name')
    player_id = data.get('player_id')  # Only for player rolls
    dice_type = data.get('dice_type')
    result = data.get('result')
    
    roll_data = {
        'roller_type': roller_type,
        'roller_name': roller_name,
        'dice_type': dice_type,
        'result': result,
        'timestamp': datetime.now().strftime('%H:%M:%S')
    }
    
    if roller_type == 'player':
        roll_data['player_id'] = player_id
    
    # Broadcast to all clients
    emit('dice_roll_result', roll_data, broadcast=True)

@socketio.on('environmental_update')
def handle_environmental_update(data):
    """Handle environmental control updates from host"""
    control_type = data.get('control_type')  # 'saturation', 'feeling', 'temperature'
    value = data.get('value')
    display_value = data.get('display_value')
    
    env_data = {
        'control_type': control_type,
        'value': value,
        'display_value': display_value,
        'timestamp': datetime.now().strftime('%H:%M:%S')
    }
    
    # Broadcast to all players
    emit('environmental_change', env_data, room='all_players')

@socketio.on('get_connected_clients')
def handle_get_connected_clients():
    """Return list of connected clients"""
    client_data = {
        'host_connected': connected_clients['host'] is not None,
        'connected_players': list(connected_clients['players'].keys()),
        'total_players': len(connected_clients['players'])
    }
    emit('connected_clients_update', client_data)

if __name__ == "__main__":
    socketio.run(app, debug=True, port=8000)