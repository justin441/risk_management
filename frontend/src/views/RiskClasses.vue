<template>
  <v-container>
    <v-layout row class="mt-4">
      <v-flex xs12 lg8 offset-lg2>
        <h2 class="headline font-weight-medium">{{ this.$route.params.name }}</h2>
        <v-dialog v-model="dialog" max-width="800" persistent scrollable @keydown.esc="close()">

          <v-tabs>
            <v-tab>
              Détails
            </v-tab>
            <v-tab-item>
              <v-card tile max-width="800">
                <v-card-title>
                  <span class="headline grey lighten-2">{{ shownItem.nom }}</span>
                </v-card-title>
                <v-card-text>
                  <v-form>
                    <v-container grid-list-md>
                      <v-layout wrap>
                        <v-flex xs12 v-if="shownItem.definition">
                          <v-text-field v-model="shownItem.definition"
                                        label="Définition"
                                        :readonly="!userCanEdit"
                                        @input="riskHasChanged=true"
                                        v-validate="{max: 200}"
                                        counter="200"
                                        name="definition"
                                        data-vv-validate-on="change"
                                        :error-messages="errors.first('definition')"
                          >

                          </v-text-field>
                        </v-flex>
                        <v-flex xs12>
                          <v-textarea v-model="shownItem.description"
                                      label="Description"
                                      box
                                      :readonly="!userCanEdit"
                                      @input="riskHasChanged=true"
                                      v-validate="{max: 500, required: true}"
                                      name="description"
                                      data-vv-validate-on="change"
                                      :error-messages="errors.first('description')"
                          >

                          </v-textarea>
                        </v-flex>
                        <v-flex xs12>
                          <v-textarea v-model="shownItem.cause"
                                      label="Cause"
                                      box
                                      :readonly="!userCanEdit"
                                      @input="riskHasChanged=true"
                                      v-validate="{required: true, max: 500}"
                                      name="cause"
                                      data-vv-validate-on="change"
                                      :error-messages="errors.first('cause')"
                          >

                          </v-textarea>
                        </v-flex>
                        <v-flex xs12>
                          <v-textarea v-model="shownItem.consequence"
                                      label="Conséquence"
                                      box
                                      :readonly="!userCanEdit"
                                      @input="riskHasChanged=true"
                                      v-validate="{required: true, max: 500}"
                                      name="consequence"
                                      data-vv-validate-on="change"
                                      :error-messages="errors.first('consequence')"
                          >

                          </v-textarea>
                        </v-flex>
                        <v-flex xs12 v-if="shownItem.couverture || riskHasChanged">
                          <v-textarea v-model="shownItem.couverture"
                                      label="Action / Couverture "
                                      box
                                      :readonly="!userCanEdit"
                                      @input="riskHasChanged=true"
                                      v-validate="{max: 500}"
                                      name="couverture"
                                      data-vv-validate-on="change"
                                      :error-messages="errors.first('couverture')"

                          >

                          </v-textarea>
                        </v-flex>
                        <v-flex xs12 v-if="shownItem.pilotage || riskHasChanged ">
                          <v-textarea v-model="shownItem.pilotage"
                                      label="Pilotage / Suivi"
                                      box
                                      :readonly="!userCanEdit"
                                      @input="riskHasChanged=true"
                                      v-validate="{max: 500}"
                                      name="pilotage"
                                      data-vv-validate-on="change"
                                      :error-messages="errors.first('pilotage')"
                          >

                          </v-textarea>
                        </v-flex>
                        <v-flex xs12 v-if="shownItem.aide || riskHasChanged">
                          <v-textarea v-model="shownItem.aide"
                                      label="Réflexion à considérer à la lecture du risque?"
                                      box
                                      :readonly="!userCanEdit"
                                      @input="riskHasChanged=true"
                                      v-validate="{max: 255}"
                                      name="aide"
                                      data-vv-validate-on="change"
                                      :error-messages="errors.first('aide')"
                          >

                          </v-textarea>
                        </v-flex>
                        <v-flex xs12 v-if="shownItem.note || riskHasChanged">
                          <v-textarea v-model="shownItem.note"
                                      label="Sommes-nous concernés"
                                      box :readonly="!userCanEdit"
                                      @input="riskHasChanged=true"
                                      v-validate="{max: 255}"
                                      name="note"
                                      data-vv-validate-on="change"
                                      :error-messages="errors.first('note')"
                                      @keypress.enter.prevent="save"
                          >

                          </v-textarea>
                        </v-flex>
                      </v-layout>
                    </v-container>
                  </v-form>
                </v-card-text>
                <v-card-actions>
                  <v-spacer></v-spacer>
                  <v-btn color="blue darken-1" flat @click="close">Fermer</v-btn>
                  <v-btn v-if="riskHasChanged" color="blue darken-1" flat @click="save">Enregistrer</v-btn>
                </v-card-actions>
              </v-card>
            </v-tab-item>
            <v-tab>
              Occurences
            </v-tab>
            <v-tab-item>
              <v-card max-width="800">
                <v-container grid-list-md fluid>
                  <v-layout row wrap>
                    <v-flex xs12 v-for="occurence in occurences.results">
                      <risk
                        :key="occurence.code_identification"
                        :risk="occurence"
                        :deletable="true"
                        @show-detail="close"
                      >
                      </risk>
                    </v-flex>
                  </v-layout>
                </v-container>
              </v-card>
            </v-tab-item>
          </v-tabs>
        </v-dialog>
        <v-list two-line class="mt-5" v-if="risks.results.length">
          <template v-for="(risk, index) in risks.results">
            <v-list-tile :key="risk.code_risque">
              <v-list-tile-content>
                <v-list-tile-title>{{ risk.nom }}</v-list-tile-title>
                <v-list-tile-sub-title>{{ risk.description}}</v-list-tile-sub-title>
              </v-list-tile-content>
              <v-spacer></v-spacer>
              <v-icon
                dark
                color="primary"
                size="20"
                @click="showItem(risk)"
              >mdi-information
              </v-icon>
            </v-list-tile>
            <v-divider
              v-if="index + 1 < risks.results.length"
              :key="index"
            ></v-divider>
          </template>
        </v-list>
        <p v-else>Vide</p>
      </v-flex>
    </v-layout>
    <div class="text-xs-center pt-2">
      <v-pagination
        v-if="pageSize < risks.count"
        v-model="page"
        :length="Math.ceil(risks.count/pageSize)"
        circle
        total-visible="4"
      ></v-pagination>
    </div>
  </v-container>

</template>

<script>
  import Risk from '../components/Risk'

  export default {
    components: {
      Risk
    },
    name: "RiskClasses",
    data() {
      return {
        // from rest_framework options
        pageSize: 10,
        page: 1,
        dialog: false,
        riskHasChanged: false,
        shownIndex: -1,
        userCanEdit: true,
        formErrors: {},
        shownItem: {
          code_risque: '',
          nom: '',
          definition: '',
          description: '',
          cause: '',
          consequence: '',
          couverture: '',
          pilotage: '',
          aide: '',
          note: ''
        },
        defaultItem: {
          code_risque: '',
          nom: '',
          definition: '',
          description: '',
          cause: '',
          consequence: '',
          couverture: '',
          pilotage: '',
          aide: '',
          note: ''

        }
      }
    },
    computed: {
      risks() {
        return this.$store.getters.risksList
      },
      occurences() {
        return this.$store.getters.occurences;
      }
    },
    created() {
      this.$store.dispatch('GET_RISKS', {
        riskClass: this.$route.params.name,
        page: this.$route.query.page || 1
      }).then(() => {
        this.page = parseInt(this.$route.query.page) || 1
      })
    },
    watch: {
      '$route'(to, from) {
        this.$store.dispatch('GET_RISKS', {
          riskClass: to.params.name,
          page: to.query.page || 1
        }).then(() => {
          this.page = parseInt(this.$route.query.page || 1)
        });

      },
      page() {
        this.$router.push(`${this.$route.path}?page=${this.page}`)
      }
    },
    methods: {
      showItem(item) {
        this.$store.dispatch('GET_RISK_OCCURENCES', item.code_risque);
        this.shownIndex = this.risks.results.indexOf(item);
        this.shownItem = Object.assign({}, item);
        this.dialog = true;
      },
      close() {
        this.dialog = false;
        this.errors.clear();
        setTimeout(() => {
          this.shownItem = Object.assign({}, this.defaultItem);
          this.shownIndex = -1;
          this.riskHasChanged = false;
        }, 300)
      },
      save() {
        this.$validator.validate().then(result => {
          if (result) {
            let item = this.risks.results[this.shownIndex];
            this.$store.dispatch('UPDATE_RISK', {
              uuid: item.code_risque,
              data: this.shownItem
            }).then(data => {
              this.risks.results.splice(this.shownIndex, 1, data);
              this.close();
            }).catch(err => {
              if (err.response.status === 400) {
                for (let f of Object.keys(err.response.data)) {
                  if (!this.errors.has(f)) {
                    this.errors.add({
                      field: f,
                      msg: err.response.data[f][0]
                    })
                  }
                }
              } else {
                this.formErrors = err.response.data;
              }
            })
          } else {
            return false
          }
        })
      }
    }
  }
</script>

<style scoped>

</style>
