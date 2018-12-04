<template>
  <v-container fluid fill-height>
    <v-layout align-center justify-center>
      <v-flex xs12 sm8 md4>
        <v-card flat tile>
          <v-toolbar flat dark color="primary">
            <v-toolbar-title class="text-xs-center">Identification</v-toolbar-title>
          </v-toolbar>
          <v-card-text>
            <v-form lazy-validation>
              <v-text-field autofocus
                            validate-on-blur
                            browser-autocomplete="off"
                            prepend-icon="mdi-account"
                            name="login"
                            label="E-mail"
                            type="email"
                            v-validate="{required: true, email: true}"
                            v-model="loginForm.email"
                            :error-messages="errors.first('email')"
                            data-vv-name="email"
                            required>

              </v-text-field>
              <v-text-field validate-on-blur
                            prepend-icon="mdi-lock"
                            name="password"
                            label="Mot de Passe"
                            type="password"
                            v-validate="{min: 8, required: true}"
                            v-model="loginForm.password"
                            :error-messages="errors.first('password')"
                            data-vv-name="password"></v-text-field>
            </v-form>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn @click="login">Connexion</v-btn>
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
        },
      }
    },
    mounted() {;
      this.$validator.localize('fr')
    },
    methods: {
      login() {
        this.$store.dispatch('AUTH_REQUEST', this.loginForm).then(resp => {
          console.log(resp)
        }).catch(err => {
          this.clear();
          console.log('erreur:', err);
        })
      },
      clear() {
        this.loginForm.email = '';
        this.loginForm.password = '';
        this.$validator.reset();

      }
    }

  }
</script>
