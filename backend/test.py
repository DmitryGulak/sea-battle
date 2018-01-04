from gameModule import SeaBattleGame

if __name__ == '__main__':
  game = SeaBattleGame()
  user = {'username': 'dimonikys', 'user_token': 'dflkjsfklwejoifwejfiowefj'}
  game.join(user)
  game.setup_ships(user, [{'wX': 1, 'wY': 1, 'pX': 0, 'pY': 0}, {'wX': 1, 'wY': 3, 'pX': 3, 'pY': 3}])
  print(game.get_info())
