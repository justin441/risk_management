import Vue from 'vue'
import VeeValidate from 'vee-validate'


Vue.use(VeeValidate, {
  locale: 'fr',
  dictionary: {
    fr: {
      name: 'fr',
      messages: {},
      attributes: {}
    }
  }
});
