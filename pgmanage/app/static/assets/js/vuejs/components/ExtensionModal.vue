<template>
  <div class="modal fade" id="postgresqlExtensionModal" tabindex="-1" role="dialog" aria-hidden="true">
    <div class="modal-dialog" role="document">
      <div class="modal-content">

        <div class="modal-header align-items-center">
          <h3 class="modal-title">{{ modalTitle }}</h3>
          <button type="button" class="close" data-dismiss="modal" aria-label="Close">
            <span aria-hidden="true"><i class="fa-solid fa-xmark"></i></span>
          </button>
        </div>

        <div class="modal-body">

          <div class="form-group row mb-1 align-items-center">
            <label for="extensionName" class="font-weight-bold col-3">Name</label>
            <select id="extensionName" class="form-control col-9" v-model="selectedExtension"
              :disabled="mode === 'Alter'">
              <option value="" disabled>Select an item...</option>
              <option v-for="(extension, index) in availableExtensions" :value="extension" :key="index">{{ extension.name
              }}</option>
            </select>

          </div>

          <div class="form-group row mb-1 align-items-center">
            <label for="extensionComment" class="font-weight-bold col-3">Comment</label>
            <textarea class="form-control col-9" id="extensionComment" disabled
              :value="selectedExtension?.comment"></textarea>
          </div>

          <div class="align-items-center form-group mb-1 row">
            <label for="extensionSchema" class="col-3 font-weight-bold">Schema</label>
            <select id="extensionSchema" class="col-9 form-control" v-model="selectedSchema"
              :disabled="!!requiredSchema || !isRelocatable">
              <option value="" disabled="">Select an item...</option>
              <option v-for="(schema, index) in schemaList" :value="schema.name" :key="index">{{ schema.name }}</option>
            </select>
          </div>

          <div class="form-group row mb-1 align-items-center">
            <label for="extensionVersions" class="font-weight-bold col-3">Version</label>
            <select id="extensionVersions" class="form-control col-9" v-model="selectedVersion">
              <option value="" disabled>Select an item...</option>
              <option v-for="(version, index) in selectedExtension?.versions" :value="version" :key="index">{{ version }}
              </option>
            </select>
          </div>

          <div id="generated_sql_div" class="mt-3" style="height: 10vh">
          </div>

        </div>

        <div class="modal-footer">
          <button type="button" class="btn btn-primary mr-2" :disabled="!selectedExtension || noUpdates"
            @click="saveExtension">
            Save
          </button>
        </div>
      </div>
    </div>
  </div>

  <GenericMessageModal ref="modal" :message="`Are you sure you want to drop extension '${treeNode.text}'?`"
    :checkboxes="[{ 'label': 'CASCADE', 'checked': false }]" :success-func="dropExtension" />
</template>


<script>
import GenericMessageModal from './GenericMessageModal.vue'

const { render } = Vue
export default {
  name: 'ExtensionModal',
  components: {
    GenericMessageModal
  },
  props: {
    mode: String,
    treeNode: Object
  },
  data() {
    return {
      availableExtensions: [],
      schemaList: '',
      selectedExtension: '',
      selectedSchema: '',
      selectedVersion: '',
      editor: '',
      tabId: window.v_connTabControl.selectedTab.id,
      databaseIndex: window.v_connTabControl.selectedTab.tag.selectedDatabaseIndex,
    }
  },
  computed: {
    generatedSQL() {
      if (!!this.selectedExtension && this.mode === 'Create') {
        const schema = !!this.selectedSchema ? `\n    SCHEMA ${this.selectedSchema}` : ''
        const version = !!this.selectedVersion ? `\n    VERSION "${this.selectedVersion}"` : ''
        return `CREATE EXTENSION ${this.selectedExtension?.name}${schema}${version};`
      } else if (this.mode === 'Alter' && !!this.selectedExtension) {
        const clauses = [];
        if (this.selectedSchema !== this.selectedExtension?.schema) {
          clauses.push(`ALTER EXTENSION ${this.selectedExtension?.name}\n    SET SCHEMA ${this.selectedSchema};`)
        }
        if (this.selectedVersion !== this.selectedExtension?.version) {
          clauses.push(`ALTER EXTENSION ${this.selectedExtension?.name}\n    UPDATE TO "${this.selectedVersion}";`)
        }
        if (clauses.length > 0) {
          return clauses.join('\n')
        } else {
          return '-- No updates.'
        }
      } else {
        return '-- No updates.'
      }
    },
    requiredSchema() {
      if (!!this.selectedExtension?.required_schema) {
        return this.selectedExtension?.required_schema
      }
    },
    isRelocatable() {
      return this.mode === 'Create' || (this.mode === 'Alter' && this.selectedExtension.relocatable);
    },
    modalTitle() {
      if (this.mode === 'Alter') return this.selectedExtension.name
      return 'Create Extension'
    },
    noUpdates() {
      return this.generatedSQL === '-- No updates.'
    }
  },
  watch: {
    requiredSchema(newValue) {
      this.selectedSchema = newValue ? newValue : ''
    },
    selectedExtension() {
      if (this.mode === 'Create') this.selectedVersion = ''
    },
    generatedSQL() {
      this.editor.setValue(this.generatedSQL)
      this.editor.clearSelection();
    }
  },
  mounted() {
    this.getAvailableExtensions()
    this.getSchemas()
    if (this.mode === 'Alter') {
      this.getExtensionDetails()
    }
    this.setupEditor()
    if (this.mode !== 'Drop') {
      $('#postgresqlExtensionModal').modal('show')
    } else {
      $('#generic_modal_message').modal('show')
    }
  },
  methods: {
    getAvailableExtensions() {
      axios.post('/get_available_extensions_postgresql/', {
        database_index: this.databaseIndex,
        tab_id: this.tabId,
      })
        .then((resp) => {
          this.availableExtensions.push(...resp.data.available_extensions)
        })
        .catch((error) => {
          console.log(error)
        })
    },
    getSchemas() {
      axios.post('/get_schemas_postgresql/', {
        database_index: this.databaseIndex,
        tab_id: this.tabId,
      })
        .then((resp) => {
          this.schemaList = resp.data.data
        })
        .catch((error) => {
          showError(error.response.data.data)
        })
    },
    saveExtension() {
      axios.post('/save_postgresql_extension/', {
        database_index: this.databaseIndex,
        tab_id: this.tabId,
        query: this.generatedSQL
      })
        .then((resp) => {
          refreshTreePostgresql(this.treeNode)
          $('#postgresqlExtensionModal').modal('hide')
        })
        .catch((error) => {
          showError(error.response.data.data);
        })
    },
    setupEditor() {
      this.editor = ace.edit('generated_sql_div');
      this.editor.setTheme("ace/theme/" + window.v_editor_theme);
      this.editor.session.setMode("ace/mode/sql");
      this.editor.setFontSize(Number(window.v_font_size));
      this.editor.setReadOnly(true);
      this.editor.$blockScrolling = Infinity;

      this.editor.setValue(this.generatedSQL)
      this.editor.clearSelection();
    },
    getExtensionDetails() {
      axios.post('/get_extension_details/', {
        database_index: this.databaseIndex,
        tab_id: this.tabId,
        ext_name: this.treeNode.text
      })
        .then((resp) => {
          this.availableExtensions.push(resp.data)
          this.selectedExtension = resp.data
          this.selectedSchema = resp.data.schema
          this.selectedVersion = resp.data.version
        })
        .catch((error) => {
          showError(error.response.data.data)
        })
    },
    dropExtension() {
      const checkedValues = this.$refs.modal.checkboxes
      const cascade = checkedValues[0].checked ? 'CASCADE' : ''
      const query = `DROP EXTENSION IF EXISTS ${this.treeNode.text} ${cascade};`
      axios.post('/save_postgresql_extension/', {
        database_index: this.databaseIndex,
        tab_id: this.tabId,
        query: query
      })
        .then((resp) => {
          refreshTreePostgresql(this.treeNode.parent)
        })
        .catch((error) => {
          showError(error.response.data.data);
        })
    }

  },
}
</script>