<template>
  <div class="modal modal-blurr" :id="modalId" tabindex="-1">
    <div class="modal-dialog modal-xl">
      <div class="modal-content">
        <div class="modal-header align-items-center">
          <h2 class="modal-title font-weight-bold">File manager</h2>
          <button type="button" class="close" data-dismiss="modal" aria-label="Close">
            <span aria-hidden="true"><i class="fa-solid fa-xmark"></i></span>
          </button>
        </div>
        <div class="modal-body p-0" style="height: 60vh">
          <div id="actions-tab" class="d-flex justify-content-between border-bottom p-1">
            <div>
              <a class="btn btn-outline-secondary btn-sm" title="Add Folder" @click="openActionsModal('addFolder')"><i
                  class="fas fa-folder-plus fa-xl"></i></a>
              <a class="btn btn-outline-secondary btn-sm" title="Add File" @click="openActionsModal('addFile')"><i
                  class="fas fa-file-circle-plus fa-xl"></i></a>
              <a :class="['btn', 'btn-outline-secondary', 'btn-sm', { 'disabled': !Object.keys(this.selectedFile).length }]"
                title="Rename Folder/File" @click="openActionsModal('rename')"><i
                  class="fas fa-thin fa-file-pen fa-xl"></i></a>
            </div>
            <div>
              <a v-if="currentView === 'table'" class="btn btn-outline-secondary btn-sm" @click="changeView"
                title="Change View"><i class="fas fa-list-ul fa-xl"></i></a>
              <a v-else class="btn btn-outline-secondary btn-sm" @click="changeView" title="Change View"><i
                  class="fas fa-grip-horizontal fa-xl"></i></a>
            </div>
          </div>

          <div class="d-flex justify-content-between align-items-center border-bottom p-1 bg-light">
            <div>
              <a :class="['btn', 'btn-outline-secondary', 'btn-sm', { 'disabled': !isChild }]" title="Click to go back"
                @click="stepBackDir"><i class="fas fa-left-long fa-xl"></i></a>
              <a class="btn btn-outline-secondary btn-sm" title="Refresh" @click="refreshManager"><i
                  class="fas fa-refresh fa-xl"></i></a>
              <a :class="['btn', 'btn-outline-secondary', 'btn-sm', { 'disabled': !isChild }]"
                title="Go back to root directory" @click="stepHomeDir"><i class="fas fa-house fa-xl"></i></a>
            </div>
            <input class="w-75 form-control" type="text" :value="currentPath" disabled>
            <a :class="['btn', 'btn-outline-secondary', 'btn-sm', { 'disabled': !Object.keys(this.selectedFile).length }]"
              title="Delete" @click="openActionsModal('delete')"><i class="fas fa-trash fa-xl"></i></a>
          </div>

          <!-- Box format for files and folders -->
          <div v-if="isGrid" class="d-flex p-2 flex-wrap">
            <div v-for="file in files" :key="file.file_name"
              :class="['text-center', 'text-break', 'btn', 'btn-outline-light', 'border-0', 'pt-3', { 'active': file === this.selectedFile }]"
              style="height: 55px;width: 80px;" @click="selectFileOrDir(file)"
              @dblclick="file.file_type === 'dir' ? getDirContent(file.file_path) : {}">
              <div class="position-relative">
                <i :class="['fas', 'fa-2xl', { 'fa-folder': file.file_type === 'dir', 'fa-file': file.file_type === 'file' }]"
                  :style="{ 'color': file.file_type === 'dir' ? '#0ea5e9' : 'rgb(105 114 118)', }"></i>
              </div>
              <span class="text-dark">{{ file.file_name }}</span>
            </div>
          </div>

          <!-- Table format for files and folders-->
          <div v-else style="overflow-y: scroll; height: 70vh;">
            <table class="table table-hover table-responsive-sm">
              <thead>
                <tr>
                  <th scope="col" style="width: 70%">Name</th>
                  <th scope="col">Size</th>
                  <th scope="col">Modified</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="file in files" :key="file.file_name" @click="selectFileOrDir(file)"
                  @dblclick="getDirContent(file.file_path)">
                  <td><i
                      :class="['fas', 'fa-2xl', { 'fa-folder': file.file_type === 'dir', 'fa-file': file.file_type === 'file' }]"
                      :style="{ 'color': file.file_type === 'dir' ? '#0ea5e9' : 'rgb(105 114 118)', }"></i> {{
                        file.file_name }}</td>
                  <td v-if="file.file_type === 'file'">{{ file.file_size }}</td>
                  <td v-if="file.file_type === 'dir'">{{ file.dir_size }} {{ file.dir_size == 1 ? 'item' : 'items' }}</td>
                  <td>{{ file.modified }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        <div class="modal-footer">
          <a :class="['btn', 'btn-secondary', 'btn-sm', 'm-0', { 'disabled': !Object.keys(this.selectedFile).length }]"
            @click="confirmSelection">
            Select</a>
        </div>
      </div>
    </div>
  </div>

  <ActionsModal :action="action" :file="selectedFile" :current-path="currentPath" ref="actionsModal"
    @action-done="refreshManager" />
</template>

<script>
import FileManagerActionsModal from './FileManagerActionsModal.vue'

export default {
  name: 'FileManager',
  components: {
    ActionsModal: FileManagerActionsModal
  },
  data() {
    return {
      currentPath: null,
      parent: false,
      files: [],
      selectedFile: {},
      action: '',
      currentView: 'grid',
      modalId: `${v_connTabControl.selectedTab.tag.tabControl.selectedTab.id}_filemanager`
    }
  },
  emits: ['changeFile'],
  computed: {
    isChild() {
      return this.parent
    },
    isGrid() {
      return this.currentView === 'grid'
    },
  },
  mounted() {
    if (!window.gv_desktopMode)
      this.getDirContent()
  },
  methods: {
    refreshManager() {
      this.getDirContent(this.currentPath)
    },
    selectFileOrDir(file) {
      this.selectedFile = file
    },
    changeView() {
      if (this.currentView === 'grid') {
        this.currentView = 'table'
      } else {
        this.currentView = 'grid'
      }

    },
    stepBackDir() {
      this.getDirContent(this.currentPath, this.parent)
    },
    stepHomeDir() {
      this.getDirContent()
    },
    getDirContent(path = null, parent_dir = null) {
      axios.post('/file_manager/get_directory/', {
        current_path: path,
        parent_dir: parent_dir
      })
        .then((resp) => {
          this.files = [...resp.data.files]
          this.currentPath = resp.data.current_path
          this.parent = resp.data.parent
          this.selectedFile = {}
        })
        .catch((error) => {
          console.log(error)
        })
    },
    openActionsModal(action) {
      this.action = action
      $(this.$refs.actionsModal.$el).modal('show')
    },
    confirmSelection() {
      this.$emit('changeFile', {
        filePath: this.selectedFile.file_path
      })
      $(`#${this.modalId}`).modal('hide')
    },
    showModal() {
      $(`#${this.modalId}`).modal('show')
    }
  }
}
</script>