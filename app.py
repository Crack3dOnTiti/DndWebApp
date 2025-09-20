from flask import Flask, jsonify, render_template, session, redirect, request
import secrets
import os
from dotenv import load_dotenv
from flask_cors import CORS
from flask_socketio import SocketIO
from routes.player_routes import player_bp
from routes.enemy_routes import enemy_bp
from routes.npc_routes import npc_bp

load_dotenv()

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")
app.secret_key = secrets.token_hex(16)

app.register_blueprint(player_bp)
app.register_blueprint(enemy_bp)
app.register_blueprint(npc_bp)

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

if __name__ == "__main__":
    socketio.run(app, debug=True, port=8000)