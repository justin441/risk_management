import Vue from 'vue'
import Vuex from 'vuex'
import axios from 'axios'
import state from './state'
import mutations from './mutations'
import actions from './actions'

Vue.use(Vuex)
axios.defaults.baseURL = 'http://127.0.0.1:8081/api/v1'

export default new Vuex.Store({
  state: state,
  mutations: mutations,
  actions: actions,
  getters: {
    isAuthenticated: state1 => !!state1.token,
    authStatus: state1 => state1.status,
    errorCode: state1 => state1.errors,
    currentUser: state1 => state1.currentUser,
    businnessUnitsList: state1 => state1.businessUnits,
    projectList: state1 => state1.projects,
    riskClassesList: state1 => state1.riskClasses,
    risksList: state1 => state1.risksList,
    occurences: state1 => state1.riskOccurences
  }
})
