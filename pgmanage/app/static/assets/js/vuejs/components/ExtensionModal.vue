<template>
  <div class="modal fade" id="createExtensionModal" tabindex="-1" role="dialog" aria-hidden="true">
    <div class="modal-dialog" role="document">
      <div class="modal-content">
        <div class="modal-header align-items-center">
          <h3 class="modal-title">Extension Create</h3>
          <button type="button" class="close" data-dismiss="modal" aria-label="Close">
            <span aria-hidden="true"><i class="fa-solid fa-xmark"></i></span>
          </button>
        </div>
        <div class="modal-body">

          <div class="form-group row mb-1 align-items-center">
            <label for="extensionName" class="font-weight-bold col-2">Name</label>
            <select id="extensionName" class="form-control col-9" v-model="selectedExtension">
              <option value="" disabled>Select an item...</option>
              <option v-for="(extension, index) in availableExtensions" :value="extension" :key="index">{{ extension.name }}</option>
            </select>

          </div>

          <div class="form-group row mb-1 align-items-center">
            <label for="extensionComment" class="font-weight-bold col-2">Comment</label>            
            <input type="text" class="form-control col-9" id="extensionComment"
            disabled :value="selectedExtension?.comment">
          </div>

          <div class="align-items-center form-group mb-1 row">
            <label for="extensionSchema" class="col-2 font-weight-bold">Schema</label>
            <select id="extensionSchema" class="col-9 form-control" v-model="schema">
              <option value="" disabled="">Select an item...</option>
              <option value="Public">Public</option>
            </select>
          </div>

          <div class="form-group row mb-1 align-items-center">
              <label for="extensionVersions" class="font-weight-bold col-2">Version</label>
              <select id="extensionVersions" class="form-control col-9" v-model="version">
                <option value="" disabled>Select an item...</option>
                <option v-for="(version, index) in selectedExtension?.versions" :value="version" :key="index">{{ version }}</option>
              </select>
          </div>

        </div>
      </div>
    </div>
  </div>

</template>


<script>
export default {
  name: 'ExtensionModal',
  data () {
    return {
      availableExtensions: '',
      selectedExtension: '',
      schema: '',
      version: '',
    }
  },
  mounted() {
    $('#createExtensionModal').on('shown.bs.modal', this.getAvailableExtensions)
  },
  computed: {
    generatedSQL() {
      return `CREATE EXTENSION ${this.selectedExtension.name};
      SCHEMA ${this.schema}
      VERSION ${this.version}`
    }
  },
  methods: {
    getAvailableExtensions() {
      axios.post('/get_available_extensions_postgresql/', {
        database_index: window.v_connTabControl.selectedTab.tag.selectedDatabaseIndex,
        tab_id: window.v_connTabControl.selectedTab.id,
      })
      .then((resp) => {
        console.log(resp)
        this.availableExtensions = resp.data.available_extensions
      })
      .catch((error) => {
        console.log(error)
      })

    }

  },
}
</script>