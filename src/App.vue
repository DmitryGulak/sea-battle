<template>
  <div id="app">
    <template v-if="!user">
      <login></login>
    </template>
    <template v-else>
      <router-view/>
    </template>
  </div>
</template>

<script>
  import EventBus from './event-bus'
  import { mapState, mapActions } from 'vuex'
  import login from './components/Login.vue'
  export default {
    name: 'app',
    computed: {
      ...mapState({
        user: state => state.user.userData
      })
    },
    methods: {
      ...mapActions(['loadUser', 'tryJoinGame'])
    },
    components: {login},
    mounted () {
      let self = this
      let gameId = this.$route.params['game_id']
      EventBus.$on('user-login', function (user) {
        console.log('USER LOGIN EMITED')
        self.tryJoinGame(gameId)
        self.$socket.emit('JOIN_GAME', {
          'game_id': gameId,
          'user': user
        })
      })
      this.loadUser()
    }
  }
</script>

<style>
  body {
    background: #fff;
  }

  #app {
    position: absolute;
    display: block;
    height: 100%;
    width: 90%;
    max-width: 400px;
    left: 0;
    right: 0;
    margin: 0 auto;
  }
</style>
