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
          <span class="primary--text text--darken-3">S'identifier </span>
        </v-btn>
        <v-btn v-if="isAuthenticated" flat color="grey">
          <v-icon left class="primary--text text--darken-3">mdi-account-circle</v-icon>
          <span class="primary--text text--darken-3">
            {{ currentUser.firstName }}
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
        <v-list-group prepend-icon="mdi-office-building">
          <v-list-tile slot="activator">
              <v-list-tile-content>
                <v-list-tile-title>Business units</v-list-tile-title>
              </v-list-tile-content>
            </v-list-tile>
            <v-list-tile
            v-for="bu in buList"
            :key="bu.uuid"
            @click=""
          >
            <v-list-tile-content>
                <v-list-tile-title>{{ bu.denomination }}</v-list-tile-title>
              </v-list-tile-content>
          </v-list-tile>
        </v-list-group>

        <v-list-group prepend-icon="mdi-folder-star">
          <v-list-tile slot="activator">
              <v-list-tile-content>
                <v-list-tile-title>Projets</v-list-tile-title>
              </v-list-tile-content>
            </v-list-tile>
          <v-list-tile
            v-for="project in projectList"
            :key="project.uuid"
            @click=""
          >
            <v-list-tile-content>
                <v-list-tile-title>{{ project.denomination }}</v-list-tile-title>
              </v-list-tile-content>
          </v-list-tile>
        </v-list-group>
      </v-list>
      <v-divider></v-divider>
      <v-list>
        <v-subheader>Base de données des risques</v-subheader>
        <v-list-tile
          v-for="classe in riskClasses"
          :key="classe.nom"
          :to="{name: 'riskClasses', params: {name: classe.nom}, query: {page: 1}}"
        >
          <v-list-tile-content>
            <v-list-tile-title>{{ classe.nom }}</v-list-tile-title>
          </v-list-tile-content>
        </v-list-tile>
      </v-list>
    </v-navigation-drawer>
  </nav>
</template>

<script>

export default {
  name: 'Navbar',
  data () {
    return {
      drawer: false
    }
  },
  methods: {
    authLogout () {
      this.$store.dispatch('AUTH_LOGOUT').then((resp) => {
        this.$router.replace('/login')
      }).catch(err => {
        console.log(err)
      })
    }
  },
  computed: {
    isAuthenticated () {
      return this.$store.getters.isAuthenticated
    },
    currentUser () {
      return this.$store.getters.currentUser
    },
    buList () {
      return this.$store.getters.businnessUnitsList
    },
     projectList (){
      return this.$store.getters.projectList
    },
    riskClasses () {
      return this.$store.getters.riskClassesList
    },
  },
  created () {
    if (this.isAuthenticated) {
      this.$store.dispatch('GET_USER')
    }
    this.$store.dispatch('GET_BU_LIST')

    this.$store.dispatch('GET_RISK_CLASSES')
  }
}
</script>

<style scoped>

</style>
