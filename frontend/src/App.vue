<template>
  <v-app>
    <Navbar />
   <v-content>
    <v-container>
      <router-view></router-view>
    </v-container>
  </v-content>
  <v-footer app></v-footer>
  </v-app>
</template>

<script>
import Navbar from './components/Navbar'
export default {
  name: 'App',
  components:{
    Navbar
  },
  data () {
    return {
      //
    }
  }
}
</script>
