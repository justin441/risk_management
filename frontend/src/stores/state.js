
export default {
  token: localStorage.getItem('bonbon') || '',
  status: '',
  errors: '',
  currentUser: {
    id: '',
    firstName: '',
    lastName: ''
  },
  businessUnits: [],
  projects: [],
  riskClasses: []
}
