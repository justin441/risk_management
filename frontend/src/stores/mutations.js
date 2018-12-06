export default {
  auth_request(state) {
      state.status = 'loading'
    },
    auth_success(state, token) {
      state.status = 'success';
      state.token = token
    },
    auth_err(state, err) {
      state.status= 'error'
      state.errors = err.request.status.toString()
    }

}
