import axios from 'axios'

export default {
  // connexion
  AUTH_REQUEST: ({ commit, dispatch }, user) => {
    return new Promise((resolve, reject) => {
      commit('request_loading');
      axios({
        method: 'POST',
        url: '/rest-auth/login/',
        data: user
      }).then(resp => {
        const token = 'Token ' + resp.data.key;
        localStorage.setItem('bonbon', token);
        axios.defaults.headers.common['Authorization'] = token;
        commit('auth_success', token);
        resolve(resp)
      }).catch(err => {
        commit('request_error', err);
        localStorage.removeItem('bonbon');
        reject(err)
      })
    })
  },
  // utilisateur connecté
  GET_USER: ({ commit, dispatch }) => {
    return new Promise((resolve, reject) => {
      commit('request_loading');
      axios({
        method: 'GET',
        url: '/user-id/'
      }).then((resp) => {
        commit('request_success');
        commit('set_user', resp.data);
        resolve(resp.data)
      }).catch(err => {
        commit('request_error');
        reject(err)
      })
    })
  },
  // deconnexion
  AUTH_LOGOUT: ({ commit }) => {
    return new Promise((resolve, reject) => {
      commit('request_loading');
      axios({
        method: 'POST',
        url: '/rest-auth/logout/'
      }).then(resp => {
        commit('auth_success', '');
        localStorage.removeItem('bonbon');
        delete axios.defaults.headers.common['Authorization'];
        resolve(resp)
      }
      ).catch(err => {
        commit('request_error', err);
        reject(err)
      })
    })
  },
  // businness unit
  GET_BU_LIST: ({ commit }) => {
    return new Promise((resolve, reject) => {
      commit('request_loading');
      axios({
        method: 'GET',
        url: '/businessunits/'
      }).then(resp => {
        commit('request_success');
        commit('set_project_list', resp.data.filter(bu => bu.projet));
        commit('set_bu_list', resp.data.filter(bu => !bu.projet));

        resolve(resp.data)
      }).catch(err => {
        console.log(err);
        reject(err)
      })
    })
  },
  // classes de risques
  GET_RISK_CLASSES: ({ commit }) => {
    return new Promise((resolve, reject) => {
      commit('request_loading');
      axios({
        method: 'GET',
        url: '/risk_classes/'
      }).then(response => {
        console.log(response.data)
        commit('request_success');
        commit('set_risk_classes_list', response.data);
        resolve(response.data)
      }).catch(error => {
        commit('request_error');
        reject(error)
      })
    })
  },
  // liste des risques
  GET_RISKS: ({commit}, riskClass) => {
    return new Promise((resolve, reject) => {
      commit('request_loading');
      axios({
        method: 'GET',
        url: '/risk_classes/' + riskClass
      }).then(response => {
        commit('request_success');
        commit('set_risks_list', response.data);
        resolve(response.data)
      }).catch(error => {
        console.log(error);
        reject(error)
      })
    })
  }
}
