<template>
  <div class="battle-page" ref="gamePage" v-if="userData != null">
    <template v-if="gameData.secondPlayer['username'] == null">
      <div class="invite-link">
        Invite your friend: <a v-bind:href="inviteLink">/game/{{gameId}}</a>
      </div>
    </template>
    <template v-if="gameStage == 'joinFail'">
      <div class="menu-page">
        <h1 class="big-title">You cannot join this game 😔</h1>
      </div>
    </template>
    <template v-if="gameStage == 'joining'">
      <div class="menu-page">
        <h1 class="big-title">Please, wait 🕰</h1>
      </div>
    </template>
    <template v-if="gameStage == 'creating'">
      <template v-if="!playerData['ships_setted']"><construct-page></construct-page></template>
      <template v-else>
        <div class="menu-page">
          <h1 class="big-title">Wait for your partner 🕐</h1>
        </div>
      </template>
    </template>
    <template v-if="gameStage == 'playing'">
      <playing-page></playing-page>
    </template>
    <template v-if="gameStage == 'win'">
      <div class="menu-page">
        <h1 class="big-title"> 🎉 {{gameData['winner']}} won! 🎉</h1>
        <button class="btn big success" @click="handleRenewGame()">⏮ Renew game ⏮</button>
      </div>
    </template>
  </div>
</template>

<script>
  import { mapState, mapActions } from 'vuex'
  import contructPage from './ConstructPage.vue'
  import PlayPage from './PlayPage.vue'
  export default {
    name: 'game-page',
    data () {
      return {
        inviteLink: location.href,
        gameId: null
      }
    },
    components: {
      'construct-page': contructPage,
      'playing-page': PlayPage
    },
    computed: {
      ...mapState({
        gameStage: state => state.game.gameStage
      }),
      'userData': {
        get () { return this.$store.state.user.userData }
      },
      'gameData': {
        get () { return this.$store.state.game }
      },
      'playerData': {
        get () { return this.$store.state.game.firstPlayer }
      }
    },
    methods: {
      ...mapActions(['tryJoinGame']),
      handleRenewGame: function () {
        this.$socket.emit('RENEW_GAME', {
          'game_id': this.gameId,
          'user': this.$store.state.user.userData
        })
      }
    },
    created () {
      this.gameId = this.$route.params['game_id']
      if (this.userData) {
        this.tryJoinGame(this.gameId)
        this.$socket.emit('JOIN_GAME', {
          'game_id': this.gameId,
          'user': this.$store.state.user.userData
        })
      }
    }
  }
</script>
