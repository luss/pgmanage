<template>
  <Teleport to="body">
    <div class="modal show" id="generic_modal_message" tabindex="-1" role="dialog" aria-hidden="true">
      <div class="modal-dialog" role="document">
        <div class="modal-content">
          <div class="modal-header align-items-center">
            <button v-if="store.closable" type="button" class="close" data-dismiss="modal" aria-label="Close"
              @click="store.hideModal">
              <span aria-hidden="true"><i class="fa-solid fa-xmark"></i></span>
            </button>
          </div>
          <div id="generic_modal_message_content" class="modal-body"
            style="white-space: pre-line; word-break: break-all">
            {{ store.message }}
            <div v-for="(checkbox, index) in store.checkboxes" :key="index" class="custom-control custom-switch">
              <input class="custom-control-input" type="checkbox" :id="`generic_modal_message_content_${index}`"
                v-model="checkbox.checked" />
              <label class="custom-control-label" :for="`generic_modal_message_content_${index}`">
                {{ checkbox.label }}
              </label>
            </div>
          </div>
          <div class="modal-footer">
            <button id="generic_modal_message_yes" type="button" class="btn btn-primary" data-dismiss="modal"
              @click="store.executeSuccess">
              Yes
            </button>
            <button id="generic_modal_message_no" type="button" class="btn btn-danger" data-dismiss="modal"
              @click="store.executeCancel">
              No
            </button>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script>
import { messageModalStore } from "../stores/stores_initializer";

export default {
  computed: {
    store() {
      return messageModalStore;
    },
  },
  mounted() {
    messageModalStore.$onAction((action) => {
      if (action.name === "showModal") {
        $("#generic_modal_message").modal({
          backdrop: "static",
          keyboard: false,
        });
      }
      if (action.name === "hideModal") {
        $("#generic_modal_message").modal("hide");
      }
    });
  },
};
</script>
