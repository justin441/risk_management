<template>
  <nav>
    <v-toolbar flat app fixed>
      <v-toolbar-side-icon class="primary--text text--darken-3" @click="drawer=!drawer"></v-toolbar-side-icon>
      <v-toolbar-title class="text-uppercase primary--text text--darken-3">
        <span class="font-weight-light">NH</span>
        <span>Risk Management</span>
      </v-toolbar-title>
      <v-spacer></v-spacer>
      <v-btn flat color="grey">
        <v-icon class="primary--text text--darken-3">mdi-magnify</v-icon>
      </v-btn>

      <v-toolbar-items class="hidden-xs-only">
        <v-btn v-if="!isAuthenticated" flat color="grey" to="/login">
          <span class="primary--text text--darken-3" >S'identifier</span>
        </v-btn>
        <v-btn v-if="isAuthenticated" flat color="grey">
          <v-icon left class="primary--text text--darken-3">mdi-account-check</v-icon>
          <span class="primary--text text--darken-3" >
            {{ user.firstName }}
          </span>
        </v-btn>
        <v-btn v-if="isAuthenticated" flat color="grey" @click="authLogout">
          <span class="primary--text text--darken-3">Déconnexion</span>
        </v-btn>
        <v-btn v-if="!isAuthenticated" flat color="grey">
          <span class="primary--text text--darken-3">Créer un compte</span>
        </v-btn>
      </v-toolbar-items>
    </v-toolbar>
    <v-navigation-drawer app v-model="drawer" class="#c5b530">
      <v-list>

      </v-list>
    </v-navigation-drawer>
  </nav>
</template>

<script>

  export default {
    name: "Navbar",
    data() {
      return {
        drawer: false,
        user: {
          firstName: '',
          lastName: ''
        }
      }

    },
    methods: {
      authLogout() {
        this.$store.dispatch('AUTH_LOGOUT').then((resp) => {
          this.$router.replace('/login')
        }).catch(err => {
          console.log(err)
        })
      }
    },
    computed: {
      isAuthenticated() {
        return this.$store.getters.isAuthenticated
      }
    },
    mounted() {
      if(this.isAuthenticated){
        this.$store.dispatch('GET_USER_ID').then(data =>{
          this.user.firstName = data.firstName;
          this.user.lastName = data.lastName
        })
      }
    }
  }
</script>

<style scoped>

</style>
