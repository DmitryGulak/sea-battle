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
      ...mapActions(['loadUser'])
    },
    components: {login},
    mounted () {
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
