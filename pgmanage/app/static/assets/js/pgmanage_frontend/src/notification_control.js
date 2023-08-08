import { createApp } from "vue";
import GenericMessageModal from "./components/GenericMessageModal.vue";
/**
 * Creates a generic message modal using Vue.js.
 * @param {string} message - The message to display in the modal.
 * @param {Function} successFunc - The function to call when the success action is triggered.
 * @param {Function} cancelFunc - The function to call when the cancel action is triggered.
 */
function createMessageModal(message, successFunc, cancelFunc) {
  const wrap_div = document.getElementById("generic-message-modal-wrap");

  wrap_div.innerHTML = `<generic-modal :message="message" :success-func="successFunc" :cancel-func="cancelFunc"></generic-modal>`;

  const app = createApp({
    components: {
      "generic-modal": GenericMessageModal,
    },
    data() {
      return {
        message: message,
        successFunc: successFunc,
        cancelFunc: cancelFunc,
      };
    },
    mounted() {
      setTimeout(() => {
        $("#generic_modal_message").on("hidden.bs.modal", () => {
          app.unmount();
        });
        $("#generic_modal_message").modal("show");
      }, 500);
    },
  });
  app.mount(`#generic-message-modal-wrap`);
}

export { createMessageModal };
