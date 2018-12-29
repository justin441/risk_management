<template>
  <v-card @click.stop="$emit('show-detail')" tile>
    <v-toolbar card dense>
      <v-toolbar-items>
        <div class="mt-3 mr-1">
          <v-icon :color="riskColor" class="mr-1">{{riskIcon}}</v-icon><span class="mt-3">{{ riskType }}</span>
        </div>
        <div v-if="verified" class="mt-3 mr-1">
          <v-icon right color="green darken-1" class="mr-1">mdi-bookmark-check</v-icon>
          <span>Verifié</span>
        </div>
        <div v-if="risk.est_obsolete" class="mt-3">
          <v-icon right color="red darken-1" class="mr-1">mdi-clock-alert</v-icon>
          <span>Obsolète</span>
        </div>
      </v-toolbar-items>
      <v-spacer></v-spacer>
      <v-btn icon>
        <v-icon v-if="deletable" @click.stop="$emit('delete-risk')">mdi-delete-forever</v-icon>
      </v-btn>
    </v-toolbar>
    <v-card-title primary-title>
      <div>
        <div class="headline">{{ risk.risque.nom}}</div>
        <span class="caption font-italic d-block">Rapporté {{ moment(risk.created).fromNow() }} par {{ risk.soumis_par.full_name }}</span>
        <span class="caption font-italic d-block" v-if="!risk.est_obsolete">Revue du risque {{ moment(risk.date_revue).fromNow() }}</span>

      </div>
    </v-card-title>
    <v-card-text>
      <div class="body-1">
        {{ risk.risque.description }}
      </div>
    </v-card-text>
  </v-card>
</template>

<script>
  import moment from 'moment'
  import fr from 'moment/locale/fr'

  moment.locale('fr');

  export default {
    name: "risk",
    data() {
      return {
        moment,
      }
    },
    props: {
      risk: {
        type: Object
      },
      deletable: {
        type: Boolean,
        required: true
      }
    },
    computed: {
      riskIcon() {
        if (this.risk.type_de_risque === 'M') {
          return 'mdi-alert'
        }
        return 'mdi-leaf'
      },
      riskType() {
        if (this.risk.type_de_risque === 'M') {
          return 'Menace'
        }
        else if (this.risk.type_de_risque === 'O') {
          return 'Opportunité'
        }
      },
      riskColor() {
        if (this.risk.type_de_risque === 'M') {
          return 'red darken-1'
        }
        return 'green darken-1'
      },
      verified() {
        return this.risk.verifie === 'verified';
      },
      riskCat() {
        if (this.risk.get_class === 'ProcessusRisque') {
          return 'processus'
        } else if (risk.get_class === 'ActiviteRisque') {
          return 'activité'
        }
      },
      target() {
        if (this.risk.get_class === 'ProcessusRisque') {
          return this.risk.processus.nom
        } else if (this.risk.get_class === 'ActiviteRisque') {
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
