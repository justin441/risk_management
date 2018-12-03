<template>
  <v-container fluid fill-height>
    <v-layout align-center justify-center>
      <v-flex xs12 sm8 md4 lg6>
        <v-card class="elevation-12">
          <v-toolbar dark color="primary">
            <v-toolbar-title justify-center>Connexion</v-toolbar-title>
          </v-toolbar>
          <v-card-text>
            <v-form>
              <v-text-field prepend-icon="mdi-account" name="login" label="E-mail" v-validate="'required|email'"
                            type="email" v-model="loginForm.email"
                            :error-messages="errors.collect('email')" data-vv-name="email" required></v-text-field>
              <v-text-field prepend-icon="mdi-lock" name="password" label="Mot de Passe" type="password"
                            v-validate="'size:8|required'" v-model="loginForm.password"
                            :error-messages="errors.collect('password')" data-vv-name="password"></v-text-field>
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
  import {mapActions} from 'vuex'

  export default {
    name: 'login',
    data() {
      return {
        loginForm: {
          email: '',
          password: ''
        },
        dictionary: {
          attributes: {
            email: 'Adresse Email'
          },
          custom: {
            password: {
              max: 'Le mot de passe doit avoir au moins 8 caratères'
            }
          }
        }
      }
    },
    mounted(){
      this.$validator.localize('fr', this.dictionary)
    },
    methods: {
      login() {
        this.$store.dispatch('AUTH_REQUEST', this.loginForm).then(resp => {
          console.log(resp)
        }).catch(err => {
          this.clear();
          console.log(err);
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
