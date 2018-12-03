import Vue from 'vue'
import Vuex from 'vuex'
import axios from 'axios'

Vue.use(Vuex);
axios.defaults.headers.post['Access-Control-Allow-Origin'] = '*';

export default new Vuex.Store({
  state: {
    token: localStorage.getItem("token") || "",
    status: '',
    authenticated: false
  },
  mutations: {
    auth_request(state) {
      state.status = 'loading'
    },
    auth_success(state, token) {
      state.status = 'success'
      state.token = token
    },
    auth_err(state) {
      state.status = 'error'
    },
    aut_logout(state) {
    }

  },
  actions: {
    AUTH_REQUEST: ({commit, dispatch}, user) => {
      return new Promise((resolve, reject) => {
        commit('auth_request');
        axios({
          method: 'POST',
          url: '/rest-auth/login',
          data: user,
          headers: {
            'Access-Control-Allow-Origin': '*',
            'Content-Type': 'application/json',
          }
        }).then(resp => {
          const token = resp.data.key;
          localStorage.setItem("token", token);
          axios.defaults.headers.common['Autorization'] = token;
          commit('auth_success', token);
          //dispatch('user_request');
          // todo: action to dispatch on successfull login
          resolve(resp)
        }).catch(err => {
          commit('auth_err', err);
          localStorage.removeItem('token');
          reject(err)
        });

      });
    },
    AUTH_LOGOUT: ({commit, dispatch}) => {
      return new Promise((resolve, reject) => {
        commit('auth_request');
        axios({
          method: 'POST',
          url: '/rest-auth/logout',
        }).then(resp => {
            commit('auth_logout');
            localStorage.removeItem('token');
            delete axios.defaults.headers.common['Authorization'];
            resolve(resp);
          }
        ).catch(err => {
          commit('auth_err');
          reject(err);
        });
      });
    }

  },
  getters: {
    isAuthenticated: state => !!state.token,
    authStatus: state => state.status
  }
})
