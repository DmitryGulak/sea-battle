import Vue from 'vue'
import Router from 'vue-router'
import GamePage from '@/components/Game'
import Menu from '@/components/Menu'

Vue.use(Router)

export default new Router({
  mode: 'history',
  base: __dirname,
  canReuse: false,
  routes: [
    {
      path: '/',
      name: 'Menu',
      component: Menu
    },
    {
      path: '/game/:game_id',
      name: 'GamePage',
      component: GamePage
    }
  ]
})
