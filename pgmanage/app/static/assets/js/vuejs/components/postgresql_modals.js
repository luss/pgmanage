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


function createExtensionModal(div_id, node, mode) {
  const parentDiv = document.getElementById(div_id);
  const newDiv = document.createElement('div')
  newDiv.id = 'extension-modal-wrap'
  newDiv.innerHTML = `<extension-modal :mode=mode :tree-node=treeNode></extension-modal>`
  parentDiv.appendChild(newDiv)

  const extensionsModal = createApp({
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
        treeNode: node
      }
    }
  });
  extensionsModal.mount(`#extension-modal-wrap`);
}
