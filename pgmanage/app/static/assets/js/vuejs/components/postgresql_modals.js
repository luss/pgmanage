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

const extensionsModal = createApp({
  components: {
    "extension-modal": Vue.defineAsyncComponent(() =>
      loadModule(
        "../static/assets/js/vuejs/components/ExtensionModal.vue",
        options
      )
    ),
  },
});

extensionsModal.mount(`#extension-modal-wrap`);
