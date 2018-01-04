import api from '../../api.js'

export default {
  state: {
    game_id: null,
    gameStage: 'joining',
    winner: null,
    firstPlayer: null,
    toSet: [],
    secondPlayer: null,
    turnBy: null,
    myTag: null,
    myShips: []
  },
  mutations: {
    watchGame (state, payload) {
      state = Object.assign(state, payload)
    },
    SOCKET_GAME_UPDATE (state, message) {
      let enemyTag = 'p1'
      let myTag = state.myTag
      if (myTag === 'p1') {
        enemyTag = 'p2'
      }
      const payload = {
        game_id: message['id'],
        gameStage: message['game_stage'],
        toSet: message['to_set'],
        turnBy: message['turn_by'],
        winner: message['winner'],
        firstPlayer: message[myTag],
        secondPlayer: message[enemyTag]
      }
      state = Object.assign(state, payload)
    }
  },
  actions: {
    createGame ({commit}, mode) {
      return new Promise((resolve, reject) => {
        api.createGame(mode, (response) => {
          let enemyTag = 'p1'
          let myTag = response.data['my_tag']
          if (myTag === 'p1') {
            enemyTag = 'p2'
          }
          const payload = {
            game_id: response.data['game']['id'],
            gameStage: response.data['game']['game_stage'],
            myTag: myTag,
            myShips: response.data['my_ships'],
            turnBy: response.data['game']['turn_by'],
            winner: response.data['game']['winner'],
            toSet: response.data['game']['to_set'],
            firstPlayer: response.data['game'][myTag],
            secondPlayer: response.data['game'][enemyTag]
          }
          commit('watchGame', payload)
          resolve(payload)
        }, (error) => { console.log('error', error); reject(error) })
      })
    },
    tryJoinGame ({commit, dispatch}, gameId) {
      api.joinGame(gameId, (response) => {
        let enemyTag = 'p1'
        let myTag = response.data['my_tag']
        if (myTag === 'p1') {
          enemyTag = 'p2'
        }
        const payload = {
          game_id: response.data['game']['id'],
          gameStage: response.data['game']['game_stage'],
          myTag: myTag,
          myShips: response.data['my_ships'],
          turnBy: response.data['game']['turn_by'],
          winner: response.data['game']['winner'],
          toSet: response.data['game']['to_set'],
          firstPlayer: response.data['game'][myTag],
          secondPlayer: response.data['game'][enemyTag]
        }
        commit('watchGame', payload)
      },
      (error) => {
        const payload = {
          gameStage: 'joinFail'
        }
        commit('watchGame', payload)
        console.log('error: ', error)
      })
    }
  }
}
