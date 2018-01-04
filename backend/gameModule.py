import redis
import uuid
import pickle
import random

r = redis.Redis(host='localhost', port=6379, db=0)

class SeaBattleGame():
  game_id = None
  game_data = None
  secret_data = None
  user = None
  with_bot = False
  bot_data = {'username': 'bot', 'user_token': '1111'}

  def __init__(self, user, game_id=None):
    if not game_id:
      self.game_id = str(uuid.uuid4()).split('-')[0]
      self.create()
    else:
      self.game_id = game_id
    self.game_data = self.get_info()
    self.with_bot = self.game_data['with_bot']
    self.secret_data = self.get_secrets()
    self.user = user

  def get_player_tag(self):
    '''
    Getting player tag by user data
    :return: player_tag
    '''
    to_search = ['p1', 'p2']
    for tag in to_search:
      player = self.secret_data[tag]
      if not player:
        continue
      if self.user['user_token'] == player['user_token']:
        return tag
    return None

  def get_info(self):
    '''
    Getting info of game session from redis
    :return: dict of game session info
    '''
    data = r.get(f'game_{self.game_id}')
    return pickle.loads(data)

  def save_info(self):
    '''
    Saving game session info to redis
    :return: True
    '''
    data = pickle.dumps(self.game_data)
    r.set(f'game_{self.game_id}', data)
    return True

  def get_secrets(self):
    '''
    Get secrets of game session from redis
    :return: dict of game session secrets
    '''
    data = r.get(f'game_secrets_{self.game_id}')
    return pickle.loads(data)

  def save_secret(self):
    '''
    Save secrets of game session to redis
    :return: True
    '''
    data = pickle.dumps(self.secret_data)
    r.set(f'game_secrets_{self.game_id}', data)
    return True

  def switch_player(self):
    '''
    Switch turn in game session to next user
    :param game_data: dict of game session data
    :return:
    '''
    if not self.with_bot:
      next_tag = 'p1'
      if self.game_data['turn_by'] == 'p1':
        next_tag = 'p2'
      else:
        next_tag = 'p1'
      self.game_data['turn_by'] = next_tag
    else:
      if self.game_data['turn_by'] == 'p1':
        self.game_data['turn_by'] = 'p2'
        self.bot_pick()
      else:
        self.game_data['turn_by'] = 'p1'

  def pick_cell(self, rI, cI):
    '''
    Pick cell of enemy sheet
    :param rI: row of sheet (int)
    :param cI: column of sheet (int)
    :return: status of pick (boolean)
    '''
    player_tag = self.get_player_tag()
    if not player_tag:
      return False
    if not (self.game_data['turn_by'] == player_tag):
      return False
    enemy_tag = 'p1'
    if player_tag == 'p1': enemy_tag = 'p2'
    _sheet = self.secret_data[enemy_tag]['sheet']
    sheet = self.game_data[enemy_tag]['sheet']
    pick_cell = _sheet[rI][cI]
    if pick_cell == 'sc':
      _ship, index = self.check_ship(self.secret_data[enemy_tag]['ships'], rI, cI)
      ship = self.game_data[enemy_tag]['ships'][index]
      ship['hp'] -= 1
      self.game_data[enemy_tag]['ships'][index] = ship
      sheet[rI][cI] = 'dc'
      won = self.calc_win(enemy_tag)
      if won:
        self.game_data['game_stage'] = 'win'
        self.game_data['winner'] = self.game_data[player_tag]['username']
      if self.with_bot and player_tag == 'p2':
        self.bot_pick()
    else:
      sheet[rI][cI] = 'mc'
      self.switch_player()
    self.game_data[enemy_tag]['sheet'] = sheet
    self.save_info()
    return True

  def setup_ships(self, ships):
    '''
    Setup ships for user
    :param ships: list of user ships (list of dicts)
    :return: status of ships setup (boolean)
    '''
    player_tag = self.get_player_tag()
    if not player_tag:
      return False
    # Set hp to ships
    for index, ship in enumerate(ships):
      ship['hp'] = ship['wX'] * ship['wY']
      ships[index] = ship
    self.secret_data[player_tag]['ships'] = ships
    public_ships = pickle.loads(pickle.dumps(ships))
    # Remove ships position and rotation for public data
    for index, ship in enumerate(public_ships):
      ship.pop('pX', None)
      ship.pop('pY', None)
      if ship['wY'] > ship['wX']:
        tmp = ship['wX']
        ship['wX'] = ship['wY']
        ship['wY'] = tmp
      public_ships[index] = ship
    self.game_data[player_tag]['ships'] = public_ships
    # Generate sheet
    _game_sheet = []
    game_sheet = []
    for row in range(0, self.game_data['wY']):
      _sheet_row = []
      sheet_row = []
      for cell in range(0, self.game_data['wY']):
        ship, index = self.check_ship(ships, row, cell)
        if ship:
          _sheet_row.append('sc')
        else:
          _sheet_row.append('ec')
        sheet_row.append('ec')
      _game_sheet.append(_sheet_row)
      game_sheet.append(sheet_row)
    self.secret_data[player_tag]['sheet'] = _game_sheet
    self.game_data[player_tag]['sheet'] = game_sheet
    self.game_data[player_tag]['ships_setted'] = True
    self.check_can_play()
    self.save_info()
    self.save_secret()
    return True

  def calc_win(self, enemy_tag):
    allHp = 0
    for ship in self.game_data[enemy_tag]['ships']:
      allHp += ship['hp']
    if allHp == 0:
      return True
    return False

  def check_can_play(self):
    if self.game_data['p1'].get('ships_setted', False) and \
      self.game_data['p2'].get('ships_setted', False):
      self.game_data['game_stage'] = 'playing'
      self.game_data['turn_by'] = 'p1'

  def check_ship(self, ships, rI, cI):
    '''
    Check ship on picked cell
    :param ships: list of user ships (list of dicts)
    :param rI: row of user sheet
    :param cI: column of user sheet
    :return: user ship and ship index OR None and -1
    '''
    for index, ship in enumerate(ships):
      if (cI <= ship['pX'] + ship['wX'] - 1) and \
         (cI >= ship['pX']) and \
         (rI <= ship['pY'] + ship['wY'] - 1) and \
         (rI >= ship['pY']):
        return ship, index
    return None, -1

  def renew(self):
    new_game_data = {
      'id': self.game_id,
      'game_stage': 'creating',
      "wX": 10,
      "wY": 10,
      "turn_by": None,
      "with_bot": self.with_bot,
      "winner": None,
      "to_set": [
        {'wX': 4, 'wY': 1},
        {'wX': 3, 'wY': 1},
        {'wX': 3, 'wY': 1},
        {'wX': 2, 'wY': 1},
        {'wX': 2, 'wY': 1},
        {'wX': 2, 'wY': 1},
        {'wX': 1, 'wY': 1},
        {'wX': 1, 'wY': 1},
        {'wX': 1, 'wY': 1},
        {'wX': 1, 'wY': 1}
      ],
      'p1': {
        "sheet": None,
        "ships": [],
        "username": self.secret_data['p1']['username'],
        "ships_setted": False
      },
      'p2': {
        "sheet": None,
        "ships": [],
        "username": self.secret_data['p2']['username'],
        "ships_setted": False
      }
    }
    new_secret_data = {
      "p1": {
        "username": self.secret_data['p1']['username'],
        "user_token": self.secret_data['p1']['user_token'],
        "ships": []
      },
      "p2": {
        "username": self.secret_data['p2']['username'],
        "user_token": self.secret_data['p2']['user_token'],
        "ships": []
      }
    }
    self.game_data = new_game_data
    self.secret_data = new_secret_data
    self.save_info()
    self.save_secret()
    if self.with_bot:
      self.setup_bot()

  def create(self):
    '''
    Setup game data and save if to redis
    :return: dict of game data
    '''
    self.game_data = {
      'id': self.game_id,
      'game_stage': 'creating',
      "wX": 10,
      "wY": 10,
      "turn_by": None,
      "with_bot": False,
      "winner": None,
      "to_set": [
        {'wX': 4, 'wY': 1},
        {'wX': 3, 'wY': 1},
        {'wX': 3, 'wY': 1},
        {'wX': 2, 'wY': 1},
        {'wX': 2, 'wY': 1},
        {'wX': 2, 'wY': 1},
        {'wX': 1, 'wY': 1},
        {'wX': 1, 'wY': 1},
        {'wX': 1, 'wY': 1},
        {'wX': 1, 'wY': 1}
      ],
      'p1': {},
      'p2': {}
    }
    self.secret_data = {
      'p1': {},
      'p2': {}
    }
    self.save_info()
    self.save_secret()
    return self.game_data

  def join(self):
    '''
    Try to join user to game session and setup user data
    :return: status of join success
    '''
    player_tag = self.get_player_tag()
    if player_tag:
      return True
    secret_payload = {
      "username": self.user['username'],
      "user_token": self.user['user_token'],
      "ships": []
    }
    payload = {
      "sheet": None,
      "ships": [],
      "username": self.user['username'],
      "ships_setted": False
    }
    if not self.secret_data.get('p1', None):
      self.game_data['p1'] = payload
      self.secret_data['p1'] = secret_payload
      self.save_info()
      self.save_secret()
      return True
    if not self.secret_data.get('p2', None):
      self.game_data['p2'] = payload
      self.secret_data['p2'] = secret_payload
      self.save_info()
      self.save_secret()
      return True
    return False

  def bot_pick(self):
    rI = random.randint(0, self.game_data['wY'] - 1)
    cI = random.randint(0, self.game_data['wX'] - 1)
    self.user = self.bot_data
    self.pick_cell(rI, cI)

  def setup_bot(self):
    secret_payload = {
      "username": self.bot_data['username'],
      "user_token": self.bot_data['user_token'],
      "sheet": [
        ['sc', 'ec', 'sc', 'ec', 'ec', 'ec', 'sc', 'sc', 'sc', 'ec'],
        ['ec', 'ec', 'ec', 'ec', 'ec', 'ec', 'ec', 'ec', 'ec', 'ec'],
        ['ec', 'sc', 'sc', 'ec', 'sc', 'sc', 'ec', 'ec', 'ec', 'ec'],
        ['ec', 'ec', 'ec', 'ec', 'ec', 'ec', 'ec', 'sc', 'sc', 'sc'],
        ['ec', 'ec', 'ec', 'ec', 'sc', 'ec', 'ec', 'ec', 'ec', 'ec'],
        ['ec', 'ec', 'ec', 'ec', 'ec', 'ec', 'ec', 'ec', 'ec', 'ec'],
        ['sc', 'ec', 'ec', 'ec', 'ec', 'sc', 'sc', 'sc', 'sc', 'ec'],
        ['ec', 'ec', 'ec', 'ec', 'ec', 'ec', 'ec', 'ec', 'ec', 'ec'],
        ['ec', 'ec', 'ec', 'ec', 'ec', 'ec', 'sc', 'sc', 'ec', 'ec'],
        ['ec', 'ec', 'ec', 'ec', 'ec', 'ec', 'ec', 'ec', 'ec', 'ec']
      ],
      "ships": [
        {'wX': 4, 'wY': 1, 'pX': 5, 'pY': 6, 'hp': 4},
        {'wX': 3, 'wY': 1, 'pX': 7, 'pY': 3, 'hp': 3},
        {'wX': 3, 'wY': 1, 'pX': 6, 'pY': 0, 'hp': 3},
        {'wX': 2, 'wY': 1, 'pX': 6, 'pY': 8, 'hp': 2},
        {'wX': 2, 'wY': 1, 'pX': 1, 'pY': 2, 'hp': 2},
        {'wX': 2, 'wY': 1, 'pX': 4, 'pY': 2, 'hp': 2},
        {'wX': 1, 'wY': 1, 'pX': 0, 'pY': 6, 'hp': 1},
        {'wX': 1, 'wY': 1, 'pX': 0, 'pY': 0, 'hp': 1},
        {'wX': 1, 'wY': 1, 'pX': 4, 'pY': 4, 'hp': 1},
        {'wX': 1, 'wY': 1, 'pX': 2, 'pY': 0, 'hp': 1}
      ]
    }
    payload = {
      "sheet": [
        ['ec', 'ec', 'ec', 'ec', 'ec', 'ec', 'ec', 'ec', 'ec', 'ec'],
        ['ec', 'ec', 'ec', 'ec', 'ec', 'ec', 'ec', 'ec', 'ec', 'ec'],
        ['ec', 'ec', 'ec', 'ec', 'ec', 'ec', 'ec', 'ec', 'ec', 'ec'],
        ['ec', 'ec', 'ec', 'ec', 'ec', 'ec', 'ec', 'ec', 'ec', 'ec'],
        ['ec', 'ec', 'ec', 'ec', 'ec', 'ec', 'ec', 'ec', 'ec', 'ec'],
        ['ec', 'ec', 'ec', 'ec', 'ec', 'ec', 'ec', 'ec', 'ec', 'ec'],
        ['ec', 'ec', 'ec', 'ec', 'ec', 'ec', 'ec', 'ec', 'ec', 'ec'],
        ['ec', 'ec', 'ec', 'ec', 'ec', 'ec', 'ec', 'ec', 'ec', 'ec'],
        ['ec', 'ec', 'ec', 'ec', 'ec', 'ec', 'ec', 'ec', 'ec', 'ec'],
        ['ec', 'ec', 'ec', 'ec', 'ec', 'ec', 'ec', 'ec', 'ec', 'ec']
      ],
      "ships": [
        {'wX': 4, 'wY': 1, 'hp': 4},
        {'wX': 3, 'wY': 1, 'hp': 3},
        {'wX': 3, 'wY': 1, 'hp': 3},
        {'wX': 2, 'wY': 1, 'hp': 2},
        {'wX': 2, 'wY': 1, 'hp': 2},
        {'wX': 2, 'wY': 1, 'hp': 2},
        {'wX': 1, 'wY': 1, 'hp': 1},
        {'wX': 1, 'wY': 1, 'hp': 1},
        {'wX': 1, 'wY': 1, 'hp': 1},
        {'wX': 1, 'wY': 1, 'hp': 1}
      ],
      "username": 'bot',
      "ships_setted": True
    }
    self.game_data['p2'] = payload
    self.game_data['with_bot'] = True
    self.secret_data['p2'] = secret_payload
    self.save_info()
    self.save_secret()
    return True
