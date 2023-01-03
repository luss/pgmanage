<template>
  <div class="row form-group">
    <div class="col-3 mr-auto">
      <form class="form" role="search">
        <label class="sr-only" for="selectServer">Search</label>
        <div class="input-group">
          <input v-model.trim="query_filter" class="form-control" id="inputSearchSettings" name="filter" placeholder="Find in settings">
        </div>
      </form>
    </div>

    <div class="col text-center" >
      <button class="btn btn-secondary" @click="showConfigHistory">Config History</button>
    </div>

    <div class="col-7">
      <label class="sr-only" for="selectConfCat">Category</label>
      <div class="input-group">
          <div class="input-group-prepend">
            <div class="input-group-text">
              Category
            </div>
            <select class="form-control" id="selectConfCat" :disabled="!!query_filter" v-model="selected">
              <option v-for="(cat, index) in categories" :value="cat" :key="index">{{ cat }}</option>
            </select>
          </div>
      </div>
    </div>
  </div>

  <div v-if="!hasResult" class="row">
    <div class="col-12"><p>No results found...</p></div>
  </div>

  <div v-else class="row">
    <div class="col-12">
      <ConfigGroup 
      v-for="setting_group in currentResult"
      :initial-group="setting_group"
      :key="setting_group.category"
      @group-change="changeData"
      />
    </div>
  </div>

  <div class="row mt-2">
    <div class="col-12 text-center">
      <button type="submit" class="btn btn-sm btn-success" @click.prevent="saveConfiguration">Save and reload configuration</button>
    </div>
  </div>
</template>

<script>
import ConfigGroup from './ConfigGroup.vue';

export default {
    name: 'Config',
    data() {
        return {
          data: '',
          updateSettings: {},
          selected: '',
          categories: '',
          query_filter: '',
        }
    },
    computed: {
      currentResult() {
        if (!!this.data) {
          if (!this.query_filter) {
          return this.data.filter((item) => item.category.match(this.selected))
          } else {
            return this.data.map((element) => {
              const rows = element.rows.filter(
                (row) => row.name.toLowerCase().includes(this.query_filter.toLowerCase()) || 
                row.desc.toLowerCase().includes(this.query_filter.toLowerCase()));
                return {...element, rows: rows}
              }).filter((element) => !!element.rows.length);
          }
        }
      },
      hasResult() {
        return !!this.currentResult?.length
      },
    },
    methods: {
      getConfiguration() {
        axios({
          method: 'post',
          url: '/configuration/',
          data: {
            data: JSON.stringify({
              "p_database_index": window.v_connTabControl.selectedTab.tag.selectedDatabaseIndex,
              "p_tab_id": window.v_connTabControl.selectedTab.id,
              "query_filter": this.query_filter
            })
          }
        })
        .then((response) => {
          this.data = response.data.settings
          this.categories = this.data.map(x => x.category)
          this.selected = this.categories[0]
        })
        .catch((error) => {
          this.data = ''
          // show modal with error message
          console.log(error)
        })
      },
      getCategories() {
        axios({method: 'post',
        url: '/configuration/categories/',
        data: { 
          data: JSON.stringify({
          "p_database_index": window.v_connTabControl.selectedTab.tag.selectedDatabaseIndex,
          "p_tab_id": window.v_connTabControl.selectedTab.id,
        })
        },
      })
        .then((response) => {
          console.log(response)
          this.categories = response.data.categories
          this.selected = this.categories[0]
        })
        .catch((error) => {
          console.log(error)
        })
      },
      changeData(e) {
        const index = this.categories.indexOf(e.changedGroup.category)
        this.data[index] = e.changedGroup
        this.updateSettings[e.updatedSetting.name] = e.updatedSetting.setting
      },
      saveConfiguration() {
        axios.post('/save_configuration/', {
          data: JSON.stringify({
          "p_database_index": window.v_connTabControl.selectedTab.tag.selectedDatabaseIndex,
          "p_tab_id": window.v_connTabControl.selectedTab.id,
          settings: this.updateSettings
        })
        })
        .then(function (response) {
          this.updateSettings = {}
          // show modal with changed settings and if setting need server restart, show it as well
          console.log(response)
        })
        .catch(function (error) {
          // if error, show modal with error
          console.log(error)
        })

      },
      showConfigHistory() {
        axios.post('/get_configuration_history/', {
          data: JSON.stringify({
            "p_database_index": window.v_connTabControl.selectedTab.tag.selectedDatabaseIndex,
            "p_tab_id": window.v_connTabControl.selectedTab.id,
          })
        })
        .then(function(response) {
          console.log(response)
        })
        .catch(function(error) {
          console.log(error)
        })
      }
    },
    mounted() {
        this.getConfiguration();
    },
    components: {
      ConfigGroup,
    }
}
</script> 
