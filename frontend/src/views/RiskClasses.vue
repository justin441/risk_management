<template>

</template>

<script>
  export default {
    name: "RiskClasses",
    data() {
      return {
        header: [
          {
            text: 'Nom',
            align:'left',
            value:'name',
          },
          {
            text: 'Description',
            align:'center',
            value:'description',
            sortable: 'false'
          },
          {
            text: 'Cause',
            align:'center',
            value:'cause',
            sortable: 'false'
          },
          {
            text: 'Conséquence',
            align:'center',
            value:'consequence',
            sortable: 'false'
          }
        ]
      }
    },
    computed: {
      risks() {
        return this.$store.getters.risksList
      }
    },
    created() {
      this.$store.dispatch('GET_RISKS', this.$route.params.name)
    },
    watch: {
      '$route'(to, from) {
        this.$store.dispatch('GET_RISKS', to.params.name)
      }
    }
  }
</script>

<style scoped>

</style>
