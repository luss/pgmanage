<template>
  <form>
    <div>
      <div class="btn-group" role="group">
        <a :class="['btn', 'btn-secondary', 'mb-2', { 'disabled': !restoreOptions.fileName }]"
          @click.prevent="createRestore">Restore</a>
        <a :class="['btn', 'btn-danger', 'mb-2', { 'disabled': !isOptionsChanged }]" @click="resetToDefault">Reset</a>
      </div>
      <ul class="nav nav-tabs" role="tablist">
        <li class="nav-item" role="presentation">
          <button class="nav-link active" id="restoreOptions_1" data-toggle="tab"
            :data-target="`#${restoreTabId}_general`" type="button" role="tab" aria-selected="true">General</button>
        </li>
        <li v-if="isNotServer" class="nav-item" role="presentation">
          <button class="nav-link" id="restoreOptions_2" data-toggle="tab" :data-target="`#${restoreTabId}_data_objects`"
            type="button" role="tab" aria-selected="false">Data/Objects
          </button>
        </li>
        <li v-if="isNotServer" class="nav-item" role="presentation">
          <button class="nav-link" id="restoreOptions_3" data-toggle="tab" :data-target="`#${restoreTabId}_options`"
            type="button" role="tab" aria-selected="false">Options
          </button>
        </li>
      </ul>
      <div class="tab-content" style="min-height:300px;">

        <div class="tab-pane fade show active" :id="`${restoreTabId}_general`" role="tabpanel">

          <div class="form-group row">
            <label for="restoreFileName" class="col-form-label col-2">FileName</label>
            <div class="col-5">
              <input v-if="desktopMode" type="file" class="form-control" id="restoreFileName" @change="onFile" nwsaveas>

              <div v-else class="input-group">
                <div class="input-group-prepend">
                  <div class="input-group-text btn btn-secondary" @click="openFileManagerModal">Select
                    a file</div>
                </div>
                <input type="text" class="form-control" :value="restoreOptions.fileName"
                  placeholder="Select file or folder" disabled>
              </div>
            </div>
          </div>

          <div v-if="!isNotServer">
            <div class="custom-control custom-switch">
              <input class="custom-control-input" type="checkbox" id="restoreOptionsEchoQueries"
                v-model="restoreOptions.echo_queries">
              <label class="custom-control-label" for="restoreOptionsEchoQueries">
                Echo all queries
              </label>
            </div>

            <div class="custom-control custom-switch">
              <input class="custom-control-input" type="checkbox" id="restoreOptionsQuiet" v-model="restoreOptions.quiet">
              <label class="custom-control-label" for="restoreOptionsQuiet">Quiet mode</label>
            </div>

          </div>

          <div v-if="isNotServer" class="form-group row">
            <label for="restoreNumberOfJobs" class="col-form-label col-2">Number of jobs</label>
            <div class="col-5">
              <input type="text" class="form-control" id="restoreNumberOfJobs"
                v-model.number="restoreOptions.number_of_jobs">
            </div>
          </div>

          <div v-if="isNotServer" class="form-group row">
            <label for="restoreRoleName" class="col-form-label col-2">Restore as:</label>
            <div class="col-5">
              <select id="restoreRoleName" class="form-control" v-model="restoreOptions.role">
                <option value="" disabled>Select an item...</option>
                <option v-for="name in roleNames" :value="name" :key="name">{{ name }}</option>
              </select>
            </div>
          </div>
        </div>

        <div class="tab-pane fade" :id="`${restoreTabId}_data_objects`" role="tabpanel">

          <fieldset>
            <legend><b>Sections</b></legend>
            <div class="custom-control custom-switch">
              <input class="custom-control-input" type="checkbox" id="restoreOptionsPreData"
                v-model="restoreOptions.pre_data" :disabled="restoreOptions.only_data || restoreOptions.only_schema">
              <label class="custom-control-label" for="restoreOptionsPreData">
                Pre-data
              </label>
            </div>

            <div class="custom-control custom-switch">
              <input class="custom-control-input" type="checkbox" id="restoreOptionsData" v-model="restoreOptions.data"
                :disabled="restoreOptions.only_data || restoreOptions.only_schema">
              <label class="custom-control-label" for="restoreOptionsData">Data</label>
            </div>

            <div class="custom-control custom-switch">
              <input class="custom-control-input" type="checkbox" id="restoreOptionsPostData"
                v-model="restoreOptions.post_data" :disabled="restoreOptions.only_data || restoreOptions.only_schema">
              <label class="custom-control-label" for="restoreOptionsPostData">
                Post-data
              </label>
            </div>
          </fieldset>

          <fieldset>
            <legend><b>Type of objects</b></legend>

            <div class="custom-control custom-switch">
              <input class="custom-control-input" type="checkbox" id="restoreOptionsOnlyData"
                v-model="restoreOptions.only_data"
                :disabled="restoreOptions.pre_data || restoreOptions.data || restoreOptions.post_data">
              <label class="custom-control-label" for="restoreOptionsOnlyData">
                Only data
              </label>
            </div>

            <div class="custom-control custom-switch">
              <input class="custom-control-input" type="checkbox" id="restoreOptionsOnlySchema"
                v-model="restoreOptions.only_schema"
                :disabled="restoreOptions.pre_data || restoreOptions.data || restoreOptions.post_data">
              <label class="custom-control-label" for="restoreOptionsOnlySchema">
                Only schema
              </label>
            </div>
          </fieldset>

          <fieldset>
            <legend><b>Do not save</b></legend>
            <div class="custom-control custom-switch">
              <input class="custom-control-input" type="checkbox" id="restoreOptionsOwner" v-model="restoreOptions.owner">
              <label class="custom-control-label" for="restoreOptionsOwner">
                Owner
              </label>
            </div>

            <div class="custom-control custom-switch">
              <input class="custom-control-input" type="checkbox" id="restoreOptionsPrivilege"
                v-model="restoreOptions.privilege">
              <label class="custom-control-label" for="restoreOptionsPrivilege">
                Privilege
              </label>
            </div>

            <div class="custom-control custom-switch">
              <input class="custom-control-input" type="checkbox" id="restoreOptionsTablespace"
                v-model="restoreOptions.tablespace">
              <label class="custom-control-label" for="restoreOptionsTablespace">
                Tablespace
              </label>
            </div>

            <div class="custom-control custom-switch">
              <input class="custom-control-input" type="checkbox" id="restoreOptionsComments"
                v-model="restoreOptions.comments">
              <label class="custom-control-label" for="restoreOptionsComments">
                Comments
              </label>
            </div>
          </fieldset>
        </div>

        <div class="tab-pane fade" :id="`${restoreTabId}_options`" role="tabpanel">
          <fieldset>
            <legend><b>Queries</b></legend>
            <div class="custom-control custom-switch">
              <input class="custom-control-input" type="checkbox" id="restoreOptionsIncludeCreateDatabase"
                v-model="restoreOptions.include_create_database">
              <label class="custom-control-label" for="restoreOptionsIncludeCreateDatabase">
                Include 'Create Database' statement
              </label>
            </div>

            <div class="custom-control custom-switch">
              <input class="custom-control-input" type="checkbox" id="restoreOptionsClean" v-model="restoreOptions.clean">
              <label class="custom-control-label" for="restoreOptionsClean">
                Clean before restore
              </label>
            </div>

            <div class="custom-control custom-switch">
              <input class="custom-control-input" type="checkbox" id="restoreOptionsSingleTransaction"
                v-model="restoreOptions.single_transaction">
              <label class="custom-control-label" for="restoreOptionsSingleTransaction">
                Single transaction
              </label>
            </div>

          </fieldset>

          <fieldset>
            <legend><b>Disable</b></legend>
            <div class="custom-control custom-switch">
              <input class="custom-control-input" type="checkbox" id="restoreOptionsTrigger"
                v-model="restoreOptions.disable_trigger">
              <label class="custom-control-label" for="restoreOptionsTrigger">
                Trigger
              </label>
            </div>

            <div class="custom-control custom-switch">
              <input class="custom-control-input" type="checkbox" id="restoreOptionsNoDataTableFail"
                v-model="restoreOptions.no_data_fail_table">
              <label class="custom-control-label" for="restoreOptionsNoDataTableFail">
                No data for failed tables
              </label>
            </div>

          </fieldset>

          <fieldset>
            <legend><b>Miscellaneous</b></legend>
            <div class="custom-control custom-switch">
              <input class="custom-control-input" type="checkbox" id="restoreOptionsVerboseMessages"
                v-model="restoreOptions.verbose">
              <label class="custom-control-label" for="restoreOptionsVerboseMessages">
                Verbose messages
              </label>
            </div>

            <div class="custom-control custom-switch">
              <input class="custom-control-input" type="checkbox" id="restoreOptionsSetSeessionAuthorization"
                v-model="restoreOptions.use_set_session_auth">
              <label class="custom-control-label" for="restoreOptionsSetSeessionAuthorization">
                Use SET SESSION AUTHORIZATION
              </label>
            </div>

            <div class="custom-control custom-switch">
              <input class="custom-control-input" type="checkbox" id="restoreOptionsExitOnError"
                v-model="restoreOptions.exit_on_error">
              <label class="custom-control-label" for="restoreOptionsExitOnError">
                Exit on error
              </label>
            </div>

          </fieldset>


        </div>

      </div>
    </div>
  </form>
  <UtilityJobs ref="jobs" />
  <FileManager ref="fileManager" @change-file="changeFilePath" />
</template>

<script>
import UtilityJobs from './UtilityJobs.vue';
import FileManager from './FileManager.vue';

export default {
  name: "RestoreTab",
  components: {
    FileManager,
    UtilityJobs
  },
  props: {
    treeNode: Object,
    restoreType: String
  },
  data() {
    return {
      roleNames: [],
      restoreOptionsDefault: {
        database: this.treeNode.tag.database,
        type: this.restoreType,
        table: "",
        schema: "",
        function: "",
        trigger: "",
        role: "",
        fileName: "",
        pre_data: false,
        post_data: false,
        only_data: false,
        only_schema: false,
        owner: false,
        privilege: false,
        tablespace: false,
        comments: false,
        include_create_database: false,
        clean: false,
        single_transaction: false,
        disable_trigger: false,
        no_data_fail_table: false,
        verbose: false,
        use_set_session_auth: false,
        exit_on_error: false,
        number_of_jobs: "",
        quiet: false,
        echo_queries: false
      },
      restoreOptions: {},
      desktopMode: window.gv_desktopMode,
      restoreTabId: window.v_connTabControl.selectedTab.tag.tabControl.selectedTab.id
    }
  },
  computed: {
    isOptionsChanged() {
      return JSON.stringify(this.restoreOptionsDefault) !== JSON.stringify(this.restoreOptions)
    },
    isNotServer() {
      return this.restoreType !== 'server'
    }
  },
  mounted() {
    this.$nextTick(() => {
      if (this.treeNode.tag.type === 'schema') {
        this.restoreOptionsDefault.schema = this.treeNode.text
      } else if (this.treeNode.tag.type === 'table') {
        this.restoreOptionsDefault.table = `"${this.treeNode.tag.schema}.${this.treeNode.text}"`
      } else if (this.treeNode.tag.type === 'trigger') {
        this.restoreOptionsDefault.trigger = `"${this.treeNode.tag.schema}.${this.treeNode.text}"`
      } else if (this.treeNode.tag.type === 'function') {
        this.restoreOptionsDefault.function = `"${this.treeNode.tag.id}"`
      }
      this.restoreOptions = { ...this.restoreOptionsDefault }
      this.getRoleNames()
    })
  },
  methods: {
    getRoleNames() {
      axios.post("/get_roles_postgresql/", {
        database_index: window.v_connTabControl.selectedTab.tag.selectedDatabaseIndex,
        tab_id: window.v_connTabControl.selectedTab.id,
      })
        .then((resp) => {
          resp.data.data.forEach(element => this.roleNames.push(element.name))
        })
        .catch((error) => {
          console.log(error)
        })
    },
    createRestore() {
      axios.post("/restore/", {
        database_index: window.v_connTabControl.selectedTab.tag.selectedDatabaseIndex,
        tab_id: window.v_connTabControl.selectedTab.id,
        data: this.restoreOptions
      })
        .then((resp) => {
          console.log(resp)
          this.$refs.jobs.startJob(resp.data.job_id)
        })
        .catch((error) => {
          console.log(error)
          showError(error.response.data.data)
        })
    },
    onFile(e) {
      const [file] = e.target.fieldset
      this.restoreOptions.fileName = file?.path
    },
    changeFilePath(event) {
      this.restoreOptions.fileName = event.filePath
    },
    openFileManagerModal() {
      this.$refs.fileManager.showModal()
    },
    resetToDefault() {
      this.restoreOptions = { ...this.restoreOptionsDefault }
    }
  }
}

</script>