<template>
  <div class="menu-page">
    <h1 class="logo">Sea Battle</h1>
    <button class="btn big" @click="handleCreateGame('friend')">Play with friend 💁🏼</button>
    <button class="btn big" @click="handleCreateGame('bot')">Play with bot 🤖</button>
    <!--<button class="btn big">Join game</button>-->
  </div>
</template>

<script>
  import { mapActions } from 'vuex'
  export default {
    name: 'menu-page',
    methods: {
      ...mapActions(['createGame']),
      handleCreateGame: function (mode) {
        let self = this
        this.createGame(mode).then((data) => {
          self.$router.push({name: 'GamePage', params: {'game_id': data['game_id']}})
        }).catch((error) => {
          console.log(error)
        })
      }
    }
  }
</script>

<style>
</style>
