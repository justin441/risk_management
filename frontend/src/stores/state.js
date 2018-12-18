
export default {
  token: localStorage.getItem('bonbon') || '',
  status: '',
  errorCode: '',
  currentUser: {
    id: '',
    firstName: '',
    lastName: ''
  },
  businessUnits: [],
  projects: [],
  riskClasses: [],
  risksList: {},
  riskOccurences: {}
}
