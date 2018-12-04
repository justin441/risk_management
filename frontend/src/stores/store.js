import Vue from 'vue'
import Vuex from 'vuex'
import axios from 'axios'
import state from './state'
import mutations from './mutations'
import actions from './actions'

Vue.use(Vuex);
axios.defaults.baseURL = 'http://127.0.0.1:8081/api/v1'

export default new Vuex.Store({
  state: state,
  mutations: mutations,
  actions: actions,
  getters: {
    isAuthenticated: state => !!state.token,
    authStatus: state => state.status
  }
})
