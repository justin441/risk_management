<template>
  <v-container fluid fill-height>
    <v-layout align-center justify-center>
      <v-flex xs12 sm8 md4>
        <v-card flat tile>
          <v-toolbar flat dark color="primary">
            <v-toolbar-title class="text-xs-center">Identification</v-toolbar-title>
          </v-toolbar>
          <v-card-text>
            <v-alert icon="mdi-alert" type="error" :value="loginError400" outline dismissible>Email ou mot de passe Invalide</v-alert>
            <v-alert icon="mdi-alert" type="error" :value="loginErrorOther" outline dismissible>Erreur de connexion</v-alert>

            <v-form>

              <v-text-field autofocus
                            browser-autocomplete="off"
                            prepend-icon="mdi-account"
                            name="email"
                            label="E-mail"
                            type="email"
                            v-validate="{required: true, email: true}"
                            v-model="loginForm.email"
                            :error-messages="errors.first('email')"
                            data-vv-validate-on="change"
                            required>

              </v-text-field>
              <v-text-field validate-on-blur
                            prepend-icon="mdi-lock"
                            name="password"
                            label="Mot de Passe"
                            type="password"
                            v-validate.disable="{required: true}"
                            data-vv-validate-on="change"
                            v-model="loginForm.password"
                            :error-messages="errors.first('password')"
                            @keypress.enter.prevent="login"
                            >

              </v-text-field>
            </v-form>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn @click="login" :disabled="!(fields.email && fields.email.valid)">Connexion</v-btn>
            <v-btn @click="clear">Reinitialiser</v-btn>
          </v-card-actions>
        </v-card>
      </v-flex>
    </v-layout>
  </v-container>
</template>

<script>

  export default {
    name: 'login',
    data() {
      return {
        loginForm: {
          email: '',
          password: ''
        }
      }
    },
    methods: {
      login() {
        this.$validator.validate().then(result => {
          if (result) {
            this.$store.dispatch('AUTH_REQUEST', this.loginForm).then(resp => {
              this.clear()
            }).catch(err => {
              this.clear();
            })
          } else {
            return false
          }
        })

      },
      clear() {
        this.loginForm.email = '';
        this.loginForm.password = '';
        this.$validator.reset();

      }
    },
    computed: {
      loginError400() {
        return this.$store.getters.authError === '400';
      },
      loginErrorOther() {
        return this.$store.getters.authError !== '' && this.$store.getters.authError !== '400';
      },
    },
  }
</script>
