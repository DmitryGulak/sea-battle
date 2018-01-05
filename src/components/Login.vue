<template>
  <div class="auth-page">
      <div class="auth-area">
        <h2>Write your login</h2>
        <input v-model="username" placeholder="Enter nickname" class="simple-input" />
        <div class="buttons-area padding">
          <button class="btn big success" @click="handleLogin">Confirm</button>
        </div>
      </div>
  </div>
</template>

<script>
  import { mapActions } from 'vuex'
  export default {
    name: 'login-page',
    data () {
      return {
        username: null
      }
    },
    methods: {
      ...mapActions(['loginUser']),
      handleLogin: function () {
        this.loginUser(this.username)
      }
    }
  }
</script>

<style>
  .auth-area {
    position: absolute;
    padding: 0 20px;
    box-sizing: border-box;
    width: 100%;
    height: 100%;
    display: flex;
    justify-content: center;
    flex-direction: column;
    align-items: center;
    align-content: center;
  }
</style>
