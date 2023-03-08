<template>
  <form>
    <div>
      <div class="btn-group" role="group">
        <a :class="['btn', 'btn-secondary', 'mb-2', { 'disabled': !backupOptions.fileName }]" @click.prevent="saveBackup">Backup</a>
        <a :class="['btn', 'btn-danger', 'mb-2', {'disabled': !isOptionsChanged}]" @click="resetToDefault">Reset</a>
      </div>

      <ul class="nav nav-tabs" role="tablist">
        <li class="nav-item" role="presentation">
          <button class="nav-link active" data-toggle="tab" :data-target="`#${backupTabId}_general`"
            type="button" role="tab" aria-selected="true">General</button>
        </li>
        <li v-if="isNotGlobals" class="nav-item" role="presentation">
          <button class="nav-link" data-toggle="tab" :data-target="`#${backupTabId}_data_objects`" type="button"
            role="tab" aria-selected="false">Data/Objects</button>
        </li>
        <li v-if="isNotGlobals" class="nav-item" role="presentation">
          <button class="nav-link" data-toggle="tab" :data-target="`#${backupTabId}_options`" type="button"
            role="tab" aria-selected="false">Options</button>
        </li>
      </ul>
      <div class="tab-content" style="min-height: 300px;">
        <div class="tab-pane fade show active" :id="`${backupTabId}_general`" role="tabpanel">
          <div class="form-group row">
            <label for="backupFileName" class="col-form-label col-2">FileName</label>
            <div class="col-5">
              <input v-if="desktopMode" type="file" class="form-control" id="backupFileName" @change="onFile" nwsaveas>

              <div v-else class="input-group">
                <div class="input-group-prepend">
                  <div class="input-group-text btn btn-secondary" @click="openFileManagerModal">Select
                    a file</div>
                </div>
                <input type="text" class="form-control" :value="backupOptions.fileName"
                  placeholder="Select file or folder" disabled>
              </div>

            </div>
          </div>
          <div v-if="isNotGlobals && backupType !== 'server'" class="form-group row">
            <label for="backupFormat" class="col-form-label col-2">Format</label>
            <div class="col-5">
              <select id="backupFormat" class="form-control" v-model="backupOptions.format">
                <option v-for="(value, key) in formats" :value="key" :key="key">{{ value }}</option>
              </select>
            </div>
          </div>
          <div v-if="isNotGlobals && backupType !== 'server'" class="form-group row">
            <label for="backupCompressionRatio" class="col-form-label col-2">Compression ratio</label>
            <div class="col-5">
              <input type="text" class="form-control" id="backupCompressionRatio" v-model="backupOptions.compression_ratio">
            </div>
          </div>
          <div v-if="isNotGlobals" class="form-group row">
            <label for="backupEncoding" class="col-form-label col-2">Encoding</label>
            <div class="col-5">
              <select id="backupEncoding" class="form-control" v-model="backupOptions.encoding">
                <option value="" disabled>Select your option</option>
                <option v-for="encoding in encodingList" :key="encoding" :value="encoding">{{ encoding }}</option>
              </select>
            </div>
          </div>
          <div v-if="isNotGlobals && backupType !== 'server'" class="form-group row">
            <label for="backupNumberOfJobs" class="col-form-label col-2">Number of jobs</label>
            <div class="col-5">
              <input type="text" class="form-control" id="backupNumberOfJobs" v-model="backupOptions.number_of_jobs"
                :disabled="backupOptions.format != 'directory'">
            </div>
          </div>
          <div class="form-group row">
            <label for="backupRoleName" class="col-form-label col-2">Role name</label>
            <div class="col-5">
              <select id="backupRoleName" class="form-control" v-model="backupOptions.role">
                <option value="" disabled>Select an item...</option>
                <option v-for="name in roleNames" :value="name" :key="name">{{ name }}</option>
              </select>
            </div>
          </div>
          <div v-if="backupType === 'server'" class="bg-hit font-italic w-25" >
            <a>The backup will be in PLAIN format.</a>
          </div>
          <fieldset v-if="!isNotGlobals">
            <legend><b>Miscellaneous</b></legend>
            <div class="custom-control custom-switch">
              <input class="custom-control-input" type="checkbox" id="backupOptionsVerboseMessages"
                v-model="backupOptions.verbose">
              <label class="custom-control-label" for="backupOptionsVerboseMessages">
                Verbose messages
              </label>
            </div>
            <div class="custom-control custom-switch">
              <input class="custom-control-input" type="checkbox" id="backupOptionsDoubleQuote"
                v-model="backupOptions.dqoute">
              <label class="custom-control-label" for="backupOptionsDoubleQuote">
                Force double quote on identifiers
              </label>
            </div>
            <div class="bg-hit font-italic w-50">
              <a>Only objects global to the entire database will be backed up, in PLAIN format</a>
          </div>
          </fieldset>
        </div>
        <div v-if="isNotGlobals" class="tab-pane fade" :id="`${backupTabId}_data_objects`" role="tabpanel">
          <fieldset v-if="backupType === 'objects'">
            <legend><b>Sections</b></legend>
            <div class="custom-control custom-switch">
              <input class="custom-control-input" type="checkbox" id="backupOptionsPreData"
                v-model="backupOptions.pre_data" :disabled="backupOptions.only_data || backupOptions.only_schema">
              <label class="custom-control-label" for="backupOptionsPreData">
                Pre-data
              </label>
            </div>
            <div class="custom-control custom-switch">
              <input class="custom-control-input" type="checkbox" id="backupOptionsData" v-model="backupOptions.data"
                :disabled="backupOptions.only_data || backupOptions.only_schema">
              <label class="custom-control-label" for="backupOptionsData">
                Data
              </label>
            </div>
            <div class="custom-control custom-switch">
              <input class="custom-control-input" type="checkbox" id="backupOptionsPostData"
                v-model="backupOptions.post_data" :disabled="backupOptions.only_data || backupOptions.only_schema">
              <label class="custom-control-label" for="backupOptionsPostData">
                Post-data
              </label>
            </div>
          </fieldset>
          <fieldset>
            <legend><b>Type of objects</b></legend>
            <div class="custom-control custom-switch">
              <input class="custom-control-input" type="checkbox" id="backupOptionsOnlyData"
                v-model="backupOptions.only_data"
                :disabled="backupOptions.pre_data || backupOptions.data || backupOptions.post_data">
              <label class="custom-control-label" for="backupOptionsOnlyData">
                Only data
              </label>
            </div>
            <div class="custom-control custom-switch">
              <input class="custom-control-input" type="checkbox" id="backupOptionsOnlySchema"
                v-model="backupOptions.only_schema"
                :disabled="backupOptions.pre_data || backupOptions.data || backupOptions.post_data">
              <label class="custom-control-label" for="backupOptionsOnlySchema">
                Only schema
              </label>
            </div>
            <div class="custom-control custom-switch">
              <input class="custom-control-input" type="checkbox" id="backupOptionsBlobs" v-model="backupOptions.blobs">
              <label class="custom-control-label" for="backupOptionsBlobs">
                Blobs
              </label>
            </div>
          </fieldset>
          <fieldset>
            <legend><b>Do not save</b></legend>
            <div class="custom-control custom-switch">
              <input class="custom-control-input" type="checkbox" id="backupOptionsOwner" v-model="backupOptions.owner">
              <label class="custom-control-label" for="backupOptionsOwner">
                Owner
              </label>
            </div>
            <div class="custom-control custom-switch">
              <input class="custom-control-input" type="checkbox" id="backupOptionsPrivilege"
                v-model="backupOptions.privilege">
              <label class="custom-control-label" for="backupOptionsPrivilege">
                Privilege
              </label>
            </div>
            <div class="custom-control custom-switch">
              <input class="custom-control-input" type="checkbox" id="backupOptionsTablespace"
                v-model="backupOptions.tablespace">
              <label class="custom-control-label" for="backupOptionsTablespace">
                Tablespace
              </label>
            </div>
            <div class="custom-control custom-switch">
              <input class="custom-control-input" type="checkbox" id="backupOptionsUnloggedTableData"
                v-model="backupOptions.unlogged_tbl_data">
              <label class="custom-control-label" for="backupOptionsUnloggedTableData">
                Unlogged table data
              </label>
            </div>
            <div class="custom-control custom-switch">
              <input class="custom-control-input" type="checkbox" id="backupOptionsComments"
                v-model="backupOptions.comments">
              <label class="custom-control-label" for="backupOptionsComments">
                Comments
              </label>
            </div>
          </fieldset>
        </div>
        <div v-if="isNotGlobals" class="tab-pane fade" :id="`${backupTabId}_options`" role="tabpanel">
          <fieldset>
            <legend><b>Queries</b></legend>
            <div class="custom-control custom-switch">
              <input class="custom-control-input" type="checkbox" id="backupOptionsColumnInserts"
                v-model="backupOptions.use_column_inserts">
              <label class="custom-control-label" for="backupOptionsColumnInserts">
                Use Column Inserts
              </label>
            </div>
            <div class="custom-control custom-switch">
              <input class="custom-control-input" type="checkbox" id="backupOptionsInsertCommands"
                v-model="backupOptions.use_insert_commands">
              <label class="custom-control-label" for="backupOptionsInsertCommands">
                Use Insert Commands
              </label>
            </div>
            <div v-if="backupType === 'objects'" class="custom-control custom-switch">
              <input class="custom-control-input" type="checkbox" id="backupOptionsCreateDbStatement"
                v-model="backupOptions.include_create_database">
              <label class="custom-control-label" for="backupOptionsCreateDbStatement">
                Include CREATE DATABASE statement
              </label>
            </div>
            <div class="custom-control custom-switch">
              <input class="custom-control-input" type="checkbox" id="backupOptionsDropDbStatement"
                v-model="backupOptions.include_drop_database" :disabled="backupOptions.only_data">
              <label class="custom-control-label" for="backupOptionsDropDbStatement">
                Include DROP DATABASE statement
              </label>
            </div>
            <div v-if="backupType === 'objects'" class="custom-control custom-switch">
              <input class="custom-control-input" type="checkbox" id="backupOptionsPartitionRoot"
                v-model="backupOptions.load_via_partition_root">
              <label class="custom-control-label" for="backupOptionsPartitionRoot">
                Load Via Partition Root
              </label>
            </div>
          </fieldset>
          <fieldset>
            <legend><b>Disable</b></legend>
            <div class="custom-control custom-switch">
              <input class="custom-control-input" type="checkbox" id="backupOptionsTrigger"
                title="disabled on object backup" v-model="backupOptions.disable_trigger"
                :disabled="!backupOptions.only_data">
              <label class="custom-control-label" for="backupOptionsTrigger">
                Trigger
              </label>
            </div>
            <div class="custom-control custom-switch">
              <input class="custom-control-input" type="checkbox" id="backupOptionsQuoting"
                v-model="backupOptions.disable_quoting">
              <label class="custom-control-label" for="backupOptionsQuoting">
                $ quoting
              </label>
            </div>
          </fieldset>
          <fieldset>
            <legend><b>Miscellaneous</b></legend>
            <div class="custom-control custom-switch">
              <input class="custom-control-input" type="checkbox" id="backupOptionsWithOid"
                v-model="backupOptions.with_oids" disabled>
              <label class="custom-control-label" for="backupOptionsWithOid">
                With OID(s)
              </label>
            </div>
            <div class="custom-control custom-switch">
              <input class="custom-control-input" type="checkbox" id="backupOptionsVerboseMessages"
                v-model="backupOptions.verbose">
              <label class="custom-control-label" for="backupOptionsVerboseMessages">
                Verbose messages
              </label>
            </div>
            <div class="custom-control custom-switch">
              <input class="custom-control-input" type="checkbox" id="backupOptionsDoubleQuote"
                v-model="backupOptions.dqoute">
              <label class="custom-control-label" for="backupOptionsDoubleQuote">
                Force double quote on identifiers
              </label>
            </div>
            <div class="custom-control custom-switch">
              <input class="custom-control-input" type="checkbox" id="backupOptionsSetSeessionAuthorization"
                v-model="backupOptions.use_set_session_auth">
              <label class="custom-control-label" for="backupOptionsSetSeessionAuthorization">
                Use SET SESSION AUTHORIZATION
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
import UtilityJobs from "./UtilityJobs.vue";
import FileManager from "./FileManager.vue";

export default {
  name: "BackupTab",
  components: {
    UtilityJobs,
    FileManager
  },
  props: {
    backupType: String,
    treeNode: Object
  },
  data() {
    return {
      roleNames: [],
      formats: {
        custom: 'Custom',
        tar: 'Tar',
        plain: 'Plain',
        directory: 'Directory'
      },
      encodingList: [
        'BIG5', 'EUC_CN', 'EUC_JIS_2004', 'EUC_JP', 'EUC_KR', 'EUC_TW', 'GB18030',
        'GBK', 'ISO_8859_5', 'ISO_8859_6', 'ISO_8859_7', 'ISO_8859_8', 'JOHAB',
        'KOI18R', 'KOI8U', 'LATIN1', 'LATIN10', 'LATIN2', 'LATIN3', 'LATIN4', 'LATIN5',
        'LATIN6', 'LATIN7', 'LATIN8', 'LATIN9', 'MULE_INTERNAL', 'SHIFT_JIS_2004', 'SJIS', 'SQL_ASCII',
        'UHC', 'UTF8', 'WIN1250', 'WIN1251', 'WIN1252', 'WIN1253', 'WIN1254', 'WIN1255', 'WIN1256',
        'WIN1257', 'WIN1258', 'WIN866', 'WIN874'
      ],
      backupOptionsDefault: {
        database: this.treeNode.tag.database,
        tables: [],
        schemas: [],
        type: this.backupType,
        role: "",
        format: this.backupType === 'objects' ? 'custom' : 'plain',
        encoding: "",
        fileName: "",
        pre_data: false,
        data: false,
        post_data: false,
        only_data: false,
        only_schema: false,
        blobs: this.backupType === 'objects' ? true : false,
        owner: false,
        privilege: false,
        tablespace: false,
        unlogged_tbl_data: false,
        comments: false,
        use_column_inserts: false,
        use_insert_commands: false,
        include_create_database: false,
        include_drop_database: false,
        load_via_partition_root: false,
        disable_trigger: false,
        disable_quoting: false,
        with_oids: false,
        verbose: true,
        dqoute: false,
        use_set_session_auth: false,
        number_of_jobs: "",
        compression_ratio: ""
      },
      backupOptions: {},
      desktopMode: window.gv_desktopMode,
      backupTabId: window.v_connTabControl.selectedTab.tag.tabControl.selectedTab.id
    }
  },
  computed: {
    isNotGlobals() {
      return this.backupType !== 'globals'
    },
    isOptionsChanged() {
      return JSON.stringify(this.backupOptionsDefault) !== JSON.stringify(this.backupOptions)
    }
  },
  mounted() {
    this.$nextTick(() => {
      if (this.treeNode.tag.type === 'schema') {
        this.backupOptionsDefault.schemas.push(this.treeNode.text)
      } else if (this.treeNode.tag.type === 'table') {
        this.backupOptionsDefault.tables.push(`"${this.treeNode.tag.schema}.${this.treeNode.text}"`)
      }
      this.backupOptions = {...this.backupOptionsDefault}
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
    saveBackup() {
      axios.post("/backup/", {
        database_index: window.v_connTabControl.selectedTab.tag.selectedDatabaseIndex,
        tab_id: window.v_connTabControl.selectedTab.id,
        data: this.backupOptions,
      })
        .then((resp) => {
          console.log(resp)
          this.$refs.jobs.startJob(resp.data.job_id)
        })
        .catch((error) => {
          console.log(error)
          showError(error.response.data.data);

        })
    },
    onFile(e) {
      const [file] = e.target.files
      console.log(file)
      this.backupOptions.fileName = file?.path
    },
    changeFilePath(event) {
      this.backupOptions.fileName = event.filePath
    },
    openFileManagerModal() {
      this.$refs.fileManager.showModal()
    },
    resetToDefault() {
      this.backupOptions = {...this.backupOptionsDefault}
    }
  }
}

</script>