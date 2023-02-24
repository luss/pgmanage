<template>
  <div class="modal fade" id="fileManagerActionsModal" tabindex="-1" role="dialog" aria-hidden="true">
  <div class="modal-dialog modal-dialog-centered" role="document">
    <div class="modal-content">
      <div class="modal-header text-center pt-2">
        <h2 class="modal-title w-100" id="exampleModalLabel">{{ modalTitle }}</h2>
      </div>
      <div class="modal-body form-group">
        <p v-if="action === 'rename'">
          <i :class="['fas', 'fa-2xl', { 'fa-folder': file.file_type === 'dir', 'fa-file': file.file_type === 'file' }]"
                  :style="{'color': file.file_type === 'dir' ? '#0ea5e9' : 'rgb(105 114 118)', }"></i>
          <span class="ml-1">{{ file.file_name }}</span>
        </p>
        <input type="text" class="form-control" v-model="name">
      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-secondary" data-dismiss="modal">Cancel</button>
        <button v-if="action === 'rename'" type="button" class="btn btn-primary" data-dismiss="modal" @click="rename">Rename</button>
        <button v-else type="button" class="btn btn-primary" data-dismiss="modal" @click="create(createdFileType)">Create</button>
      </div>
    </div>
  </div>
  </div>
</template>

<script>
export default {
  name: 'ActionsModal',
  props: {
    action: {
      type: String,
      required: true
    },
    file: {
      type: Object,
      required: true
    },
    currentPath: {
      type: String,
      default: null
    }
  },
  data() {
    return {
      name: '',
    }
  },
  emits: ['actionDone'],
  computed: {
    modalTitle() {
      if (this.action === 'addFolder') {
        return 'New folder'
      } else if (this.action == 'addFile') {
        return 'New file'
      } else {
        return 'Rename'
      }
    },
    createdFileType() {
      if (this.action === 'addFolder') {
        return 'dir'
      }else {
        return 'file'
      }
    }
  },
  methods: {
    rename() {
      axios.post('/file_manager/rename/', {
        path: this.file?.file_path,
        name: this.name
      })
      .then((resp) => {
        this.name = ''
        this.$emit('actionDone')
      })
      .catch((error) => {
        console.log(error)
      })
    },
    create(type) {
      axios.post('/file_manager/create/', {
        path: this.currentPath,
        name: this.name,
        type: type
      })
      .then((resp) => {
        this.name = ''
        this.$emit('actionDone')
      })
      .catch((error) => {
        console.log(error)
      })
    },

  },

}

</script>