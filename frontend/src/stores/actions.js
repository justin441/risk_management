import axios from "axios";

export default {
  //connexion
  AUTH_REQUEST: ({commit, dispatch}, user) => {
    return new Promise((resolve, reject) => {
      commit('auth_request');
      axios({
        method: 'POST',
        url: '/rest-auth/login/',
        data: user,
      }).then(resp => {
        const token = 'Token ' + resp.data.key;
        localStorage.setItem("bonbon", token);
        axios.defaults.headers.common['Authorization'] = token;
        commit('auth_success', token);
        resolve(resp)
      }).catch(err => {
        console.log(err)
        commit('auth_err', err);
        localStorage.removeItem('bonbon');
        reject(err)
      });

    });
  },
  AUTH_LOGOUT: ({ commit }) => {
    return new Promise((resolve, reject) => {
      commit('auth_request');
      axios({
        method: 'POST',
        url: '/rest-auth/logout/'
      }).then(resp => {
          commit('auth_success', '');
          localStorage.removeItem('user')
          localStorage.removeItem('bonbon');
          delete axios.defaults.headers.common['Authorization'];
          resolve(resp);
        }
      ).catch(err => {
        commit('auth_err', err);
        reject(err);
      });
    });
  },
  GET_USER_ID: ({commit, dispatch}) => {
    return new Promise((resolve, reject) => {
      commit('auth_request');
      axios({
        method: 'GET',
        url: '/user-id/'
      }).then((resp) => {
        resolve(resp.data)
      }).catch(err => {
        console.log(err);
        reject(err)
      })
    })
  },
  GET_BU_LIST: ({commit, dispatch}) => {
    return new Promise((resolve, reject) => {

    })
  }
}
