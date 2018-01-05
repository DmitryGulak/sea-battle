from flask import Flask, render_template, send_from_directory, g, request, make_response, jsonify
from flask_socketio import SocketIO, send, join_room, leave_room
import jwt
import config
import uuid
import os
from gameModule import SeaBattleGame

app = Flask(__name__, template_folder = "../dist")
app.config['SECRET_KEY'] = config.SECRET
app._static_folder = os.path.abspath("../dist/static/")
socketio = SocketIO(app)

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers',
                         'Content-Type,Authorization,X-Access-Token')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    response.headers.add('Cache-Control', 'no-cache, no-store, must-revalidate')
    response.headers.add('Pragma', 'no-cache')
    response.headers.add('Expires', '0')
    response.headers.add('Cache-Control', 'public, max-age=0')
    return response

def get_user_token():
  token = request.cookies.get('user_token', None)
  if not token:
    token = request.headers.get('X-Access-Token', None)
  return token

def parse_token(token):
    try:
        user = jwt.decode(token, config.SECRET, algorithms=['HS256'])
    except jwt.DecodeError:
        return None
    return user

def try_get_user():
    token = get_user_token()
    try:
        user = jwt.decode(token, config.SECRET, algorithms=['HS256'])
    except jwt.DecodeError:
        return None
    return user

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def index(path):
  return render_template('index.html')

@app.route('/static/<path:filename>')
def send_static(filename):
    print('try send static')
    return send_from_directory('../dist/static/', filename)

@app.route('/api/get_user')
def get_user():
  user_data = try_get_user()
  return jsonify(user_data)

@app.route('/api/set_user', methods=['POST'])
def set_user():
  data = request.json
  username = data.get('username', 'player')
  if username == "":
    username = 'player'
  payload = {
    'username': username,
    'user_token': uuid.uuid4().hex
  }
  token = jwt.encode(payload, config.SECRET)
  response = make_response(jsonify(payload))
  response.set_cookie('user_token', token)
  return response

@app.route('/api/create_game', methods=['POST'])
def create_game():
  data = request.json
  mode = data.get('mode', 'friend')
  user = try_get_user()
  game = SeaBattleGame(user=user)
  if mode == 'bot':
    game.setup_bot()
  game.join()
  player_tag = game.get_player_tag()
  secret_data = game.get_secrets()
  payload = {
    'game': game.get_info(),
    'my_tag': player_tag,
    'my_ships': secret_data[player_tag]['ships']
  }
  return jsonify(payload)

@app.route('/api/join_game', methods=['POST'])
def join_game():
  data = request.json
  game_id = data.get('game_id', None)
  if game_id == None:
    return jsonify({'error': 'cannot join'})
  user = try_get_user()
  if not user:
    return jsonify({'error': 'cannot join'})
  game = SeaBattleGame(user=user, game_id=game_id)
  joined = game.join()
  if not joined:
    return jsonify({'error': 'cannot join'})
  player_tag = game.get_player_tag()
  secret_data = game.get_secrets()
  payload = {
    'game': game.get_info(),
    'my_tag': player_tag,
    'my_ships': secret_data[player_tag]['ships']
  }
  return jsonify(payload)

@socketio.on('JOIN_GAME')
def socket_join_game(json):
  user = json['user']
  if not json.get('game_id', None):
    return
  game = SeaBattleGame(game_id=json['game_id'], user=user)
  player_tag = game.get_player_tag()
  if player_tag:
    join_room(game.game_id)
    socketio.emit('GAME_UPDATE', game.get_info(), room=game.game_id, broadcast=True)

@socketio.on('SETUP_SHIPS')
def socket_setup_ships(json):
  user = json['user']
  game = SeaBattleGame(game_id=json['game_id'], user=user)
  player_tag = game.get_player_tag()
  if player_tag:
    game.setup_ships(json['ships'])
    socketio.emit('GAME_UPDATE', game.get_info(), room=game.game_id, broadcast=True)

@socketio.on('PICK_CELL')
def socket_pick_cell(json):
  user = json['user']
  game = SeaBattleGame(game_id=json['game_id'], user=user)
  player_tag = game.get_player_tag()
  if player_tag:
    game.pick_cell(json['rI'], json['cI'])
    socketio.emit('GAME_UPDATE', game.get_info(), room=game.game_id, broadcast=True)

@socketio.on('RENEW_GAME')
def socket_renew_game(json):
  user = json['user']
  game = SeaBattleGame(game_id=json['game_id'], user=user)
  player_tag = game.get_player_tag()
  if player_tag:
    print('renew game')
    game.renew()
    socketio.emit('GAME_UPDATE', game.get_info(), room=game.game_id, broadcast=True)

if __name__ == "__main__":
  socketio.run(app, debug=config.DEBUG)
