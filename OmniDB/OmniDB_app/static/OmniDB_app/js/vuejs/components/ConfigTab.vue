<template>
  <div class="form-row form-group">
    <div class="col-2">
      <form class="form" role="search">
        <label class="sr-only" for="selectServer">Search</label>
        <div class="input-group">
          <input v-model.trim="query_filter" class="form-control" id="inputSearchSettings" name="filter" placeholder="Find in settings">
        </div>
      </form>
    </div>

    <div class="col-auto">
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

    <div class="col-5">
      <label class="sr-only" for="selectConf">Config History</label>
      <div class="input-group">
          <div class="input-group">
            <div class="input-group-text">
              Config History
            </div>
            <select class="form-control text-truncate" id="selectConf" v-model="selectedConf">
              <option disabled value="">Please select one</option>
              <option v-for="(config, index) in configHistory" :value="config" :key="index" :title="config.commit_comment">
                {{ index }} {{ truncateText(config, 50) }}
              </option>
            </select>
            <button class="btn btn-sm btn-success ml-2" @click="applyOldConfig">Apply</button>
            <button class="btn btn-sm btn-danger ml-2">Delete</button>
          </div>
      </div>
    </div>
  </div>

  <div v-if="appliedSettings.restartPending" class="row">
  <div class="col-12">
    <div id="alert-configuration" class="alert alert-warning alert-dismissible" role="alert">
      <h2><i class="fa fa-warning fa-fw"></i>WARNING</h2>
      <p> Some changes are pending and PostgreSQL should be restarted:</p>
      <ul>
      <li v-for="change in appliedSettings.restartChanges" :key="change.name">
        {{change.name}}
      </li>
      </ul>
    </div>
  </div>
  </div>

  <div v-if="hasUpdatedValues">
    <div class="row">
      <div class="col-12">
        <div id="ok-configuration" class="alert alert-success alert-dismissible" role="alert">
          <button type="button" class="close" aria-label="Close" @click="appliedSettings.data = ''"><span aria-hidden="true">&times;</span></button>
          <p class="text-center">The following changes have been applied:</p>
          <table class="table table-sm">
          <tr>
            <th width="30%">Name</th>
            <th width="30%">Prev. value</th>
            <th width="40%">New value</th>
          </tr>
          <tr v-for="setting in appliedSettings.data" :key="setting.name">
            <td>{{ setting.name }}</td>
            <td>{{setting.previous_setting}}</td>
            <td><b>{{ setting.setting }}</b></td>
          </tr>
          </table>
        </div>
      </div>
    </div>
  </div>

  <div v-if="!hasResult" class="row">
    <div class="col-12"><p>No results found...</p></div>
  </div>

  <div v-else class="row">
    <div class="col-12">
      <ConfigTabGroup 
        v-for="setting_group in currentResult"
        :initial-group="setting_group"
        :key="setting_group.category"
        @group-change="changeData"
      />
    </div>
  </div>

  <div class="row mt-2 mb-2">
    <div class="col-12 text-center">
      <button type="submit" class="btn btn-sm btn-success" @click.prevent="confirmConfig">Save and reload configuration</button>
    </div>
  </div>

  <!--Modal for commit messaging and returning result-->
  <div class="modal fade" :id="`config_modal_${tabId}`" tabindex="-1" role="dialog" aria-hidden="true">
      <div class="modal-dialog" role="document">
        <div class="modal-content">
          <div class="modal-header justify-content-center">
            <h5 class="modal-title">Config Management</h5>
          </div>
          <div class="modal-body">
            <div class="form-group">
              <label for="commit_message">Commit Comment</label>
              <input v-model="commitComment" id="commit_message" class="form-control" placeholder="Short description of your changes(optional)">
            </div>
          </div>
          <div class="modal-footer">
            <button id="config_modal_button" type="button" class="btn btn-success" data-dismiss="modal" @click="saveConfiguration">Save configuration</button>
          </div>
        </div>
      </div>
    </div>
</template>

<script>
import ConfigTabGroup from './ConfigTabGroup.vue';

export default {
    name: 'Config',
    components: {
      ConfigTabGroup,
    },
    data() {
        return {
          data: '',
          updateSettings: {},
          selected: '',
          categories: '',
          query_filter: '',
          configHistory: '',
          selectedConf: '',
          commitComment: '',
          tabId: window.v_connTabControl.selectedTab.id,
          appliedSettings: {
            data: '',
            restartChanges: '',
            restartPending: ''
          }
        }
    },
    computed: {
      currentResult() {
        if (!!this.data) {
          if (!this.query_filter) {
          return this.data.filter((item) => item.category === this.selected)
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
      hasUpdatedValues() {
        return !!this.appliedSettings.data.length
      }
    },
    mounted() {
        this.getCategories();
        this.getConfiguration();
        this.getConfigHistory();
        this.getSettingsStatus();
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
        })
        .catch((error) => {
          this.data = ''
          showError(error.response.data)
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
          this.categories = response.data.categories
          this.selected = this.categories[0]
        })
        .catch((error) => {
          showError(error.response.data)
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
          settings: this.updateSettings,
          commit_comment: this.commitComment
        })
        })
        .then((response) => {
          console.log(response)
          this.updateSettings = {}
          this.commitComment = ''
          this.appliedSettings.data = response.data.settings
          this.getConfigHistory()
          this.getConfiguration()
          this.getSettingsStatus()
        })
        .catch((error) =>  {
          showError(error.response.data)
        })

      },
      getConfigHistory() {
        axios.post('/get_configuration_history/', {
          data: JSON.stringify({
            "p_database_index": window.v_connTabControl.selectedTab.tag.selectedDatabaseIndex,
            "p_tab_id": window.v_connTabControl.selectedTab.id,
          })
        })
        .then((response) => {
          this.configHistory = response.data.config_history.map((el) => {
            return {...el, start_time: moment(el.start_time).format('MMMM D, YYYY hh:mm A')}
          })
        })
        .catch((error) => {
          showError(error.response.data)
        })
      },
      confirmConfig() {
        $(`#config_modal_${this.tabId}`).modal();
      },
      applyOldConfig() {
        this.updateSettings = this.selectedConf.config_snapshot
        this.saveConfiguration()
      },
      truncateText(input, max_length) {
        const text = `${input.start_time} - ${input.user} - ${input.commit_comment}`
        return (text.length > max_length) ? text.slice(0, max_length-1) + '...' : text
      },
      getSettingsStatus() {
        axios.post('/configuration/status/', {
          data: JSON.stringify({
            "p_database_index": window.v_connTabControl.selectedTab.tag.selectedDatabaseIndex,
            "p_tab_id": window.v_connTabControl.selectedTab.id,
          })
        })
        .then((response) => {
          this.appliedSettings.restartPending = response.data.restart_pending
          this.appliedSettings.restartChanges = response.data.restart_changes
        })
        .catch((error) => {
          showError(error.response.data)
        })
      }
    },

}
</script> 
