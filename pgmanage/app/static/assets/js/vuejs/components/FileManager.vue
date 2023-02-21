<template>
    <div class="modal modal-blurr" id="filemanager-modal" tabindex="-1" style="display: block;">
    <div class="modal-dialog modal-xl">
      <div class="modal-content">
        <div class="modal-header align-items-center">
          <h6 class="modal-title font-weight-bold">File manager</h6>
          <button type="button" class="close" data-dismiss="modal" aria-label="Close">
            <span aria-hidden="true"><i class="fa-solid fa-xmark"></i></span>
          </button>
        </div>
        <div class="modal-body p-0">
          <div id="actions-tab" class="d-flex justify-content-between border-bottom p-1">
            <div>
              <a class="btn btn-outline-secondary btn-sm" title="Add Folder"><i class="fas fa-folder-plus fa-xl"></i></a>
              <a class="btn btn-outline-secondary btn-sm" title="Add File"><i class="fas fa-file-circle-plus fa-xl"></i></a>
              <a class="btn btn-outline-secondary btn-sm" title="Rename Folder/File"><i class="fas fa-thin fa-file-pen fa-xl"></i></a>
            </div>
            <div>
              <a class="btn btn-outline-secondary btn-sm"><i class="fas fa-list-ul fa-xl"></i></a>  /
              <a class="btn btn-outline-secondary btn-sm"><i class="fas fa-grip-horizontal fa-xl"></i></a>
            </div>
          </div>
      
          <div class="d-flex justify-content-between align-items-center border-bottom p-1 bg-light">
            <div>
              <a class="btn btn-outline-secondary btn-sm"><i class="fas fa-left-long fa-xl"></i></a>
              <a class="btn btn-outline-secondary btn-sm"><i class="fas fa-refresh fa-xl"></i></a>
              <a class="btn btn-outline-secondary btn-sm"><i class="fas fa-house fa-xl"></i></a>
            </div>
            <input class="w-75 form-control" type="text">
            <a class="btn btn-outline-secondary btn-sm"><i class="fas fa-trash fa-xl"></i></a>
          </div>



          <!-- BOX FOR files/directories -->
          <div class="d-flex p-2 flex-wrap" style="height: 400px;">
            <div class="text-center btn btn-outline-light border-0" style="height: 55px;width: 80px;">
              <div class="position-relative">
                <i class="fas fa-folder fa-2xl" style="color: #0ea5e9"></i>
              </div>
              <span class="text-dark">media</span>
            </div>
            <div class="text-center btn btn-outline-light border-0" style="height: 55px;width: 80px;">
              <div class="position-relative">
                <i class="fas fa-folder fa-2xl" style="color: #0ea5e9"></i>
              </div>
              <span class="text-dark">media</span>
            </div>
            <div class="text-center btn btn-outline-light border-0" style="height: 55px;width: 80px;">
              <div class="position-relative">
                <i class="fas fa-folder fa-2xl" style="color: #0ea5e9"></i>
              </div>
              <span class="text-dark">media</span>
            </div>
            <div class="text-center btn btn-outline-light border-0" style="height: 55px;width: 80px;">
              <div class="position-relative">
                <i class="fas fa-folder fa-2xl" style="color: #0ea5e9"></i>
              </div>
              <span class="text-dark">media</span>
            </div>
            <div class="text-center btn btn-outline-light border-0" style="height: 55px;width: 80px;">
              <div class="position-relative">
                <i class="fas fa-folder fa-2xl" style="color: #0ea5e9"></i>
              </div>
              <span class="text-dark">media</span>
            </div>
            <div class="text-center btn btn-outline-light border-0" style="height: 55px;width: 80px;">
              <div class="position-relative">
                <i class="fas fa-folder fa-2xl" style="color: #0ea5e9"></i>
              </div>
              <span class="text-dark">media</span>
            </div>
            <div class="text-center btn btn-outline-light border-0" style="height: 55px;width: 80px;">
              <div class="position-relative">
                <i class="fas fa-folder fa-2xl" style="color: #0ea5e9"></i>
              </div>
              <span class="text-dark">media</span>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <a class="btn btn-secondary btn-sm m-0"> Select</a>
        </div>
      </div>
    </div>
  </div>

</template>

<script>
// this filemanager should have two options:
// if desktop mode - open native filemanager
// if server mode - open custom filemanager
// will be 2 types of files: - file and directory, 
// and depending of what type render proper icons.
// from backend need to get name, size, date of creation.

export default {
  name: 'FileManager',
  data() {
    return {}
  },
  mounted() {
    // call backend api and get file
  },
  methods: {
    renameInstance() {
    },
    deleteFileOrDir() {
    },
    refreshManager() {
    },
    selectFileOrDir() {
    },
    changeFilesView() {
    },
    stepBack() {
    },
    stepHome() {

    },

    
  }
}

</script>

<style>
</style>