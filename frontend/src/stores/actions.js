import axios from "axios";

export default {
  AUTH_REQUEST: ({commit, dispatch}, user) => {
      return new Promise((resolve, reject) => {
        commit('auth_request');
        axios({
          method: 'POST',
          url: '/rest-auth/login/',
          data: user,
          headers: {
            'Content-Type': 'application/json',

          },
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
}
