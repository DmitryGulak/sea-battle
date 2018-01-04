// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import App from './App'
import store from './store'
import VueSocketio from 'vue-socket.io'
import router from './router'
import './assets/main.css'

Vue.config.productionTip = false
if (process.env.NODE_ENV === 'development') {
  Vue.use(VueSocketio, 'http://localhost:5000', store)
} else {
  Vue.use(VueSocketio, '/', store)
}
/* eslint-disable no-new */
new Vue({
  el: '#app',
  router,
  template: '<App/>',
  components: { App },
  store
})
