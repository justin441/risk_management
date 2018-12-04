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
        <v-btn flat color="grey" >
          <span class="primary--text text--darken-3">S'identifier</span>
        </v-btn>
        <v-btn flat color="grey">
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
      }

    }
  }
</script>

<style scoped>

</style>
