export default {
  request_loading (state) {
    state.status = 'loading'
  },
  request_error (state, err) {
    state.status = 'error'
    state.errors = err.request.status.toString()
  },
  request_success (state) {
    state.status = 'success'
  },
  auth_success (state, token) {
    state.status = 'success'
    state.token = token
  },
  set_user (state, data) {
    state.currentUser.id = data.id
    state.currentUser.firstName = data.firstName
    state.currentUser.lastName = data.lastName
  },
  set_bu_list (state, data) {
    state.businessUnits = data
  },
  set_project_list(state, data){
    state.projects = data
  },
  set_risk_classes_list (state, data) {
    state.riskClasses = data
  }
}
