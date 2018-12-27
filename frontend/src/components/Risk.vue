<template>
  <v-layout xs12>
    <v-card @click.stop="$emit('show-detail')" tile>
    <v-toolbar card dense flat>
      <v-icon :color="riskColor" >{{riskIcon}}</v-icon>
      <div v-if="verified">
        <v-icon left color="green darken-1">mdi-shield-check</v-icon><span>Verifié</span>
      </div>
      <v-spacer></v-spacer>
      <v-btn icon>
        <v-icon v-if="deletable" @click.stop="$emit('delete-risk')">mdi-delete-forever</v-icon>
      </v-btn>
    </v-toolbar>
    <v-card-title primary-title>
      <div>
        <div class="headline">{{ risk.risque.nom}}</div>
        <span class="caption font-italic">Rapporté {{ moment(risk.created).fromNow() }} par {{ risk.soumis_par.__str__ }}</span><br>
        <span class="caption font-italic" v-if="!risk.est_obsolete">Revue du risque {{ moment(risk.date_revue).fromNow() }}</span><br>
        <span class="body-1 red--text text--darken-1 " v-if="risk.est_obsolete">Revue Obsolète</span><br>

      </div>
    </v-card-title>
    <v-card-text>

    </v-card-text>
  </v-card>
  </v-layout>
</template>

<script>
  import moment from 'moment'
  import fr from 'moment/locale/fr'
  moment.locale('fr');

  export default {
    name: "risk",
    data () {
      return {
        moment,
      }
    },
    props: {
      risk: {
        type: Object
      },
      deletable:{
        type: Boolean,
        required: true
      }
    },
    computed: {
      riskIcon() {
        if(this.risk.type_de_risque === 'M'){
          return 'mdi-alert'
        }
        return 'mdi-leaf'
      },
      riskColor()  {
        if(this.risk.type_de_risque === 'M'){
          return 'red darken-1'
        }
        return 'green darken-1'
      },
      verified()  {
        return this.risk.verifie === 'verified';
      },
      riskCat()  {
        if(this.risk.get_class === 'ProcessusRisque'){
          return 'processus'
        }
        else if (risk.get_class === 'ActiviteRisque') {
          return 'activité'
        }
      },
      target()  {
        if (this.risk.get_class === 'ProcessusRisque') {
          return this.risk.processus.nom
        }
        else if (this.risk.get_class === 'ActiviteRisque') {
          return this.risk.activite.nom
        }
      }
    },
    mounted() {
  }
  }
</script>

<style scoped>

</style>
