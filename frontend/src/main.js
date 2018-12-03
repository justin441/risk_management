import '@babel/polyfill'
import Vue from 'vue'
import './plugins/vuetify'
import './plugins/veevalidate'
import App from './App.vue'
import router from './router'
import store from './store'
import 'roboto-fontface/css/roboto/roboto-fontface.css'
import '@mdi/font/css/materialdesignicons.css'
import axios from 'axios'

const token = localStorage.getItem('token');

if (token){
  axios.defaults.headers.common['Autorization'] = token
}

Vue.config.productionTip = false

new Vue({
  router,
  store,
  render: h => h(App)
}).$mount('#app')
