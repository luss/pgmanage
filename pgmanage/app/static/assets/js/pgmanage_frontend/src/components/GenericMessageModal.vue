<template>
  <Teleport to="body">
  <div class="modal show" id="generic_modal_message" tabindex="-1" role="dialog" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered" role="document">
      <div class="modal-content">
        <div class="modal-header align-items-center">
          <button v-if="closable" type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close">
          
          </button>
        </div>
        <div id="generic_modal_message_content" class="modal-body" style='white-space: pre-line; word-break: break-all;'>
          {{ message }}
          <div v-for="(checkbox, index) in checkboxes" :key="index" class="form-check form-switch">
            <input class="form-check-input" type="checkbox" :id="`generic_modal_message_content_${index}`"
              v-model="checkbox.checked">
            <label class="form-check-label" :for="`generic_modal_message_content_${index}`">
              {{ checkbox.label }}
            </label>
          </div>
        </div>
        <div class="modal-footer">
          <button id="generic_modal_message_yes" type="button" class="btn btn-primary" data-bs-dismiss="modal"
            @click="successFunc">Yes</button>
          <button id="generic_modal_message_no" type="button" class="btn btn-danger" data-bs-dismiss="modal"
            @click="cancelFunc">No</button>
        </div>
      </div>
    </div>
  </div>
</Teleport>
</template>


<script>
export default {
  props: {
    successFunc: {
      type: Function,
      default: () => { }
    },
    cancelFunc: {
      type: Function,
      default: () => { }
    },
    message: {
      type: String,
    },
    checkboxes: {
      type: Array,
      default: () => []
    },
    closable: {
      type: Boolean,
      default: true
    }
  },
}
</script>