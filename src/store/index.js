import api from '../api.js'
import Vue from 'vue'
import Vuex from 'vuex'
import gameModule from './modules/moduleGame'
import createLogger from 'vuex/dist/logger'
Vue.use(Vuex)
const debug = process.env.NODE_ENV !== 'production'

const userModule = {
  state: {
    userData: null
  },
  mutations: {
    watchUser (state, user) {
      state.userData = user
    }
  },
  actions: {
    loginUser ({commit}, username) {
      api.setUser({
        'username': username
      }, (response) => {
        commit('watchUser', response.data)
      }, (error) => { console.log('error: ', error) })
    },
    loadUser ({commit}) {
      api.getUser(
        (response) => {
          commit('watchUser', response.data)
        }, (error) => { console.log('error: ', error) })
    }
  }
}

export default new Vuex.Store({
  strict: debug,
  plugins: debug ? [createLogger()] : [],
  modules: {
    user: userModule,
    game: gameModule
  }
})
