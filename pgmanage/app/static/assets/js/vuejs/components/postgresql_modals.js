const jobDetailModal = createApp({
  components: {
    "job-detail": Vue.defineAsyncComponent(() =>
      loadModule(
        "/static/assets/js/vuejs/components/UtilityJobsJobDetail.vue",
        options
      )
    ),
  },
});

jobDetailModal.mount("#utility-job-detail-wrap");

function createExtensionModal(node, mode) {
  const wrap_div = document.getElementById("extension-modal-wrap");

  wrap_div.innerHTML = `<extension-modal :mode=mode :tree-node=treeNode></extension-modal>`;

  const app = createApp({
    components: {
      "extension-modal": Vue.defineAsyncComponent(() =>
        loadModule(
          "../static/assets/js/vuejs/components/ExtensionModal.vue",
          options
        )
      ),
    },
    data() {
      return {
        mode: mode,
        treeNode: node,
      };
    },
    mounted() {
      setTimeout(() => {
        $("#postgresqlExtensionModal").on("hidden.bs.modal", () => {
          app.unmount();
        });
        $("#generic_modal_message").on("hidden.bs.modal", () => {
          app.unmount();
        });
      }, 500);
    },
  });
  app.mount(`#extension-modal-wrap`);
}
